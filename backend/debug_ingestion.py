
import logging
from app.services.knowledge_service import knowledge_service

# Setup logging
logging.basicConfig(level=logging.INFO)

REPORT = """
Post Mortem: Payment Gateway Failure
Date: 2024-03-20
Symptom: High latency on transaction processing.
Action: Restarted the payment pod.
Outcome: Latency returned to normal.
"""

def debug():
    print("Testing Ingestion Logic...")
    try:
        result = knowledge_service.ingest_fault_report(REPORT, "debug_script")
        print("\n--- Result ---")
        print(result)
        
        if result:
            print("\n✅ Success")
        else:
            print("\n❌ Failed (Empty Result)")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    debug()
