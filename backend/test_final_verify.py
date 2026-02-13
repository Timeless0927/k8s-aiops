
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_result(name, success, details):
    icon = "✅" if success else "❌"
    print(f"\n{icon} **{name}**: {'SUCCESS' if success else 'FAILED'}")
    if details:
        print(f"   {details}")

def test_chat():
    print("\n--- Testing 1. Chat (Agent) ---")
    payload = {
        "messages": [{"role": "user", "content": "Hello, are you online?"}],
        # "model": "gpt-4-turbo"  <-- Removed to use backend default from DB
    }
    try:
        start = time.time()
        resp = requests.post(f"{BASE_URL}/chat/chat", json=payload, timeout=30)
        duration = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("response", "")
            print_result("Chat API", True, f"Response ({duration:.2f}s): {content[:100]}...")
            return True
        else:
            print_result("Chat API", False, f"Status: {resp.status_code}, Error: {resp.text}")
            return False
    except Exception as e:
        print_result("Chat API", False, f"Exception: {e}")
        return False

def test_ingest():
    print("\n--- Testing 2. Knowledge Ingestion (RAG) ---")
    text = "Post-Mortem: At 10:00 AM, the payment service crashed due to OOM. We increased memory limit to 512Mi. Service recovered at 10:05 AM."
    payload = {
        "text": text,
        "source": "verification_script"
    }
    try:
        start = time.time()
        resp = requests.post(f"{BASE_URL}/knowledge/ingest", json=payload, timeout=30)
        duration = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            structured = data.get("structured_data", {})
            print_result("Knowledge Ingestion", True, f"Structured ({duration:.2f}s): {json.dumps(structured, indent=2)}")
            return True
        else:
            print_result("Knowledge Ingestion", False, f"Status: {resp.status_code}, Error: {resp.text}")
            return False
    except Exception as e:
        print_result("Knowledge Ingestion", False, f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Final System Verification...")
    print(f"Target: {BASE_URL}")
    
    chat_ok = test_chat()
    ingest_ok = test_ingest()
    
    if chat_ok and ingest_ok:
        print("\n🎉 ALL SYSTEMS GO! The Agent is fully operational.")
    else:
        print("\n⚠️ SYSTEM PARTIALLY OPERATIONAL. Check errors above.")
