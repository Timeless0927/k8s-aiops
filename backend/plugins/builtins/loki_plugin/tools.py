import httpx
import json
import logging
import time
import urllib.parse
from app.core.config import settings

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
        
        base_url = settings.GRAFANA_URL.rstrip('/')
        return f"{base_url}/explore?orgId=1&left={encoded_json}"
    except Exception as e:
        logger.error(f"Failed to build Grafana link: {e}")
        return ""

async def run_loki_query(query: str, limit: int = 10, mode: str = "logs") -> str:
    """
    Executes a LogQL query against Loki.
    - limit: Max lines (default 10).
    - mode: 'logs' (default) or 'stats' (returns counts/patterns).
    """
    # ... (URL setup) ...
    base_url = settings.LOKI_URL.rstrip('/')
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
                short_text = response.text[:200]
                return f"Error: Loki returned status {response.status_code}. Details: {short_text}"
            
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
                return f"No logs found for this query in the last 1 hour.{link_text}"
            
            # Format logs for LLM readability
            # Stricter Token Limits (Option A)
            logs = []
            total_chars = 0
            MAX_TOTAL_CHARS = 2000 # Reduced from 8000
            MAX_LINE_CHARS = 500   # Reduced from 1000
            
            for stream_entry in result:
                values = stream_entry.get("values", [])
                for ts, line in values:
                    if len(line) > MAX_LINE_CHARS:
                        line = line[:MAX_LINE_CHARS] + "...(truncated)"
                    
                    logs.append(line)
            
            # Stats Mode (Option C)
            if mode == "stats":
                count = len(logs)
                # Simple keyword analysis
                error_count = sum(1 for l in logs if "error" in l.lower() or "exception" in l.lower())
                return f"""📊 **Log Statistics**
- **Total Lines Found**: {count}
- **Potential Errors**: {error_count}
- **Query**: `{query}`

💡 **Tip**: Use `run_loki_query(query="{query} |= \\"error\\"", limit=5)` to see error details.
{link_text}"""

            # Dedup
            unique_logs = list(dict.fromkeys(logs))
            
            final_output = []
            for log in unique_logs[:limit]:
                if total_chars + len(log) > MAX_TOTAL_CHARS:
                    final_output.append(f"\n⚠️ **Output Truncated** (Exceeded {MAX_TOTAL_CHARS} chars). Use stricter filters.")
                    break
                final_output.append(log)
                total_chars += len(log)

            return "\n".join(final_output) + link_text

    except httpx.ConnectError:
        return f"Error: Could not connect to Loki at {base_url}. Please check configuration."
    except Exception as e:
        logger.error(f"Loki execution error: {e}")
        return f"Error executing query: {str(e)}"
