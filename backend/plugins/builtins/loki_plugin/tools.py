import httpx
import json
import logging
import time
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_loki_query(query: str, limit: int = 50) -> str:
    """
    Executes a LogQL query against Loki to retrieve logs.
    """
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
            if not result:
                return "No logs found for this query in the last 1 hour."
            
            # Format logs for LLM readability
            logs = []
            for stream_entry in result:
                # labels = stream_entry.get("stream", {})
                values = stream_entry.get("values", [])
                for ts, line in values:
                    # Timestamp in nanoseconds -> readable? 
                    # LLM can handle raw timestamp or we can ignore it to save context.
                    # Let's keep it simple: just the log line.
                    # Or maybe formatted: [ts] line
                    logs.append(line)
            
            # Return top N lines distinct
            # Sometimes logs are duplicated in streams
            unique_logs = list(set(logs))
            return "\n".join(unique_logs[:limit])

    except httpx.ConnectError:
        return f"Error: Could not connect to Loki at {base_url}. Please check configuration."
    except Exception as e:
        logger.error(f"Loki execution error: {e}")
        return f"Error executing query: {str(e)}"
