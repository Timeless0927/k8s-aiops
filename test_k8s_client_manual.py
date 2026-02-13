import asyncio
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.services.k8s_client import k8s_client

def test_log_retrieval():
    # command from user screenshot (example)
    # user ran: kubectl logs cu-iot-edge-gateway-service-7ff57d7bf6-xj9mg -n edge-env-test --tail 30
    # Let's try to run a simple 'get pods' first to verify connectivity
    
    print("1. Testing connectivity...")
    res = k8s_client.execute_cli("get pods -A")
    print(f"Result (First 100 chars): {res[:100]}")
    
    print("\n2. Testing Specific Log Command (Mocking User's scenario)")
    # Replace with a pod that likely exists or use 'get pods' to find one
    # Since we don't know the exact pod name that is consistently there, we will just try to run the exact string user provided 
    # assuming the user is running this on the SAME machine where the agent is.
    
    pod_name = "cu-iot-edge-gateway-service-7ff57d7bf6-xj9mg" 
    namespace = "edge-env-test"
    cmd = f"logs {pod_name} -n {namespace} --tail 30"
    
    print(f"Running: kubectl {cmd}")
    res = k8s_client.execute_cli(cmd)
    
    print(f"\n--- OUTPUT START ---")
    print(res)
    print(f"--- OUTPUT END ---")

if __name__ == "__main__":
    test_log_retrieval()
