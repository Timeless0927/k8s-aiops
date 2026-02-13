import requests
import json
import time

URL = "http://127.0.0.1:8000/api/v1/knowledge/ingest"

SAMPLE_REPORT = """
Post Mortem: Database Latency Spike
Date: 2024-03-15
Author: SRE Team

Incident began at 14:00 due to a sudden increase in write queries from the new 'analytics' service.
The primary database CPU spiked to 99%, causing timeouts for the main application.
We identified the heavy queries and temporarily blocked the analytics service IP.
After blocking, CPU dropped to 20%.
We then optimized the indexes and re-enabled the service at 15:30.
"""

def test_ingest():
    print(f"Testing Ingestion at {URL}...")
    try:
        response = requests.post(URL, json={"text": SAMPLE_REPORT, "source": "test_script"})
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Ingestion Successful!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            structured = data.get("structured_data", {})
            if structured.get("symptom") and structured.get("action"):
                print("\n✅ Valid Structure Detected.")
            else:
                print("\n⚠️ Warning: Missing expected fields in structured data.")
        else:
            print(f"\n❌ Request Failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    test_ingest()
