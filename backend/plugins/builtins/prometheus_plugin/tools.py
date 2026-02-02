import httpx
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_prometheus_query(query: str, step: str = "1m") -> str:
    """
    Executes a PromQL query against the configured Prometheus instance.
    """
    base_url = settings.PROMETHEUS_URL.rstrip('/')
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
            
            # Check API status
            if data.get("status") != "success":
                 return f"Error: Prometheus query failed. Response: {json.dumps(data)}"
            
            result = data.get("data", {}).get("result", [])
            
            if not result:
                return "No metrics found for this query."
            
            # Return raw JSON
            return json.dumps(result, ensure_ascii=False)

    except httpx.ConnectError:
        return f"Error: Could not connect to Prometheus at {base_url}. Please check if the service is reachable or port-forward is active."
    except Exception as e:
        logger.error(f"Prometheus execution error: {e}")
        return f"Error executing query: {str(e)}"
