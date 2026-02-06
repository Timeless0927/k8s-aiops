import httpx
import json
import logging
from app.core.monitoring_config import MonitoringConfigManager

logger = logging.getLogger(__name__)

import urllib.parse
import json

# ... (Previous imports) ...

def _build_grafana_link(query: str) -> str:
    """Helper to build Grafana Explore URL"""
    try:
        # Default range: last 1h
        explore_data = {
            "datasource": "Prometheus",
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

async def run_prometheus_query(query: str, step: str = "1m") -> str:
    """
    Executes a PromQL query against the configured Prometheus instance.
    Returns JSON result + Grafana Deep Link.
    """
    base_url = MonitoringConfigManager.get_config().prometheus_url.rstrip('/')
    url = f"{base_url}/api/v1/query"
    params = {"query": query}
    
    logger.info(f"Prometheus Query: {query} (URL: {url})")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code != 200:
                return f"Error: Prometheus returned status {response.status_code}. Details: {response.text}"
            
            try:
                data = response.json()
            except Exception as e:
                return f"Error: Failed to parse Prometheus JSON response: {str(e)}"
            
            if data.get("status") != "success":
                 return f"Error: Prometheus query failed. Response: {json.dumps(data)}"
            
            result = data.get("data", {}).get("result", [])
            
            # Generate Deep Link
            grafana_link = _build_grafana_link(query)
            link_text = f"\n\n🔗 [View Graph in Grafana]({grafana_link})" if grafana_link else ""

            if not result:
                return f"No metrics found for this query.{link_text}"
            
            # Return raw JSON + Link
            return json.dumps(result, ensure_ascii=False) + link_text

    except httpx.ConnectError:
        return f"Error: Could not connect to Prometheus at {base_url}. Please check if the service is reachable or port-forward is active."
    except Exception as e:
        logger.error(f"Prometheus execution error: {e}")
        return f"Error executing query: {str(e)}"
