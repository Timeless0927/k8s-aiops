import httpx
import json
import logging
import time
import urllib.parse
from app.core.monitoring_config import MonitoringConfigManager

logger = logging.getLogger(__name__)

def _build_grafana_link(query: str) -> str:
    """Helper to build Grafana Explore URL"""
    try:
        # Default range: last 1h
        explore_data = {
            "datasource": "Loki",
            "queries": [{"refId": "A", "expr": query}],
            "range": {"from": "now-1h", "to": "now"}
        }
        
        # Grafana requires URL-encoded JSON in 'left' param
        json_str = json.dumps(explore_data)
        encoded_json = urllib.parse.quote(json_str)
        
        base_url = MonitoringConfigManager.get_config().grafana_url.rstrip('/')
        return f"{base_url}/explore?orgId=1&left={encoded_json}"
    except Exception as e:
        logger.error(f"Failed to build Grafana link: {e}")
        return ""

# Import at module level if possible, or inside function to avoid circular imports? 
# Module level is fine here.
from app.services.log_forensics import LogForensicsService

async def run_loki_query(query: str, limit: int = 10, mode: str = "logs", auto_analyze: bool = True) -> str:
    """
    Executes a LogQL query against Loki.
    - auto_analyze: If True, AI will automatically analyze logs for Root Cause (Smart Tool).
    """
    # ... (URL setup) ...
    base_url = MonitoringConfigManager.get_config().loki_url.rstrip('/')
    url = f"{base_url}/loki/api/v1/query_range"
    
    # Default time range: last 1 hour
    end_time = int(time.time() * 1e9)
    start_time = end_time - (3600 * 1000000000)
    
    params = {
        "query": query, 
        "limit": limit,
        "start": start_time,
        "end": end_time
    }
    
    logger.info(f"Loki Query: {query} (URL: {url})")
    
    headers = {"X-Scope-OrgID": "1"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                return f"Error: Loki returned status {response.status_code}."
            
            try:
                data = response.json()
            except Exception as e:
                return f"Error: Failed to parse Loki JSON response: {str(e)}"
            
            if data.get("status") != "success":
                 return f"Error: Loki query failed. Response: {json.dumps(data)}"
            
            result = data.get("data", {}).get("result", [])
            
            # Generate Deep Link
            grafana_link = _build_grafana_link(query)
            link_text = f"\n\n🔗 [View Logs in Grafana]({grafana_link})" if grafana_link else ""

            if not result:
                return f"No logs found.{link_text}"
            
            # --- AGGREGATION LOGIC (Simplified for Analysis) ---
            full_logs_for_ai = []
            preview_logs = []
            
            for stream_entry in result:
                values = stream_entry.get("values", [])
                for ts, line in values:
                    full_logs_for_ai.append(line)
                    if len(preview_logs) < 10: # Only preview 10 lines
                        preview_logs.append(line[:200] + "..." if len(line) > 200 else line)
            
            # 1. Preview Output
            preview_text = "\n".join(preview_logs)
            if len(full_logs_for_ai) > 10:
                preview_text += f"\n... ({len(full_logs_for_ai)-10} more lines hidden)"
            
            # 2. Smart Analysis
            analysis_text = ""
            if auto_analyze and full_logs_for_ai:
                # Analyze combined text (limit to 10k chars to be safe for local LLM)
                combined_text = "\n".join(full_logs_for_ai)[:10000]
                structured, _ = LogForensicsService.analyze_logs(combined_text)
                if structured:
                     analysis_text = f"""
🧠 **Smart Analysis (Auto-Generated)**:
- **Incident**: {structured.get('incident_type')}
- **Cause**: {structured.get('root_cause')}
- **Fix**: {structured.get('suggestion')}
"""
            
            return f"**Logs Preview**:\n{preview_text}\n{analysis_text}{link_text}"

    except httpx.ConnectError:
        return f"Error: Could not connect to Loki at {base_url}. Please check configuration."
    except Exception as e:
        logger.error(f"Loki execution error: {e}")
        return f"Error executing query: {str(e)}"
