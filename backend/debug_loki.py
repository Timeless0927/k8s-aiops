import asyncio
import logging
import sys
import time
import httpx

# Add . to sys.path
sys.path.append(".")

from plugins.builtins.loki_plugin.tools import run_loki_query

logging.basicConfig(level=logging.INFO)

async def main():
    print("Testing Loki Query...")
    
    base_url = "http://10.0.41.135:32350"
    
    tenants = ["fake", "user", "main", "docker", "promtail", "fluent-bit", "anonymous"]
    
    print(f"\n--- Checking Specific Query: {{namespace=\"doris\"}} ---")
    
    # Extended list of potential tenant IDs
    tenants = [
        "fake", "user", "main", "docker", "admin", "loki", "dev", "prod", 
        "1", "0", "1001", "monitoring", "system", "doris", "k8s"
    ]
    
    # Also try no header
    headers_list = [{"X-Scope-OrgID": t} for t in tenants]
    headers_list.append({}) # No header
    
    query = '{namespace="doris"}'
    
    for headers in headers_list:
        tenant_name = headers.get("X-Scope-OrgID", "No-Header")
        # print(f"Trying {tenant_name}...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Query Range
                params = {
                    "query": query,
                    "limit": 1,
                    "start": int(time.time() * 1e9) - (3600 * 1000000000), # Last 1h
                    "end": int(time.time() * 1e9)
                }
                resp = await client.get(f"{base_url}/loki/api/v1/query_range", params=params, headers=headers, timeout=3.0)
                
                if resp.status_code == 200:
                    data = resp.json().get("data", {}).get("result", [])
                    if data:
                        print(f"!!! SUCCESS with Tenant: '{tenant_name}' !!!")
                        print(f"Found {len(data)} streams.")
                        break
                    # else:
                    #    print(f"[{tenant_name}] 200 OK but no data.")
                else:
                    pass
                    # print(f"[{tenant_name}] Failed: {resp.status_code}")
                    
        except Exception as e:
            print(f"[{tenant_name}] Error: {e}")

    # 2. Try Query with 24h range
    try:
        print("\nQuerying last 24h...")
        # Broad query
        query = '{namespace=~".+"}' 
        # Manually calling run_loki_query? 
        # Note: run_loki_query in tools.py has hardcoded 1h.
        # We should probably modify tools.py to allow time range or just test raw httpx here.
        
        # Let's test raw httpx here to be sure, then patch tools.py
        end_time = int(time.time() * 1e9)
        start_time = end_time - (24 * 3600 * 1000000000) # 24 hours
        
        params = {
            "query": query,
            "limit": 10,
            "start": start_time,
            "end": end_time
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/loki/api/v1/query_range", params=params, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("data", {}).get("result", [])
                print(f"Found {len(results)} streams.")
                if results:
                    print("Sample:", results[0].get("values", [])[0])
            else:
                print(f"Query failed: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
