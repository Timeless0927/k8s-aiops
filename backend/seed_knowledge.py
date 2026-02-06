import asyncio
from app.services.knowledge_service import knowledge_service

CONTENT = """
Resolution for JVM GC Overhead Limit Exceeded:
The service 'order-service' was experiencing frequent Full GC cycles causing CPU spikes.
Root Cause: Default MaxMetaspaceSize (256m) was insufficient for the new dynamic class loading requirements.
Solution:
1. Updated Deployment env vars: JAVA_OPTS="-XX:MaxMetaspaceSize=512m"
2. Verified heap dump showed no memory leaks, just class metadata exhaustion.
"""

METADATA = {
    "topic": "JVM GC Loop Fixed",
    "symptoms": "High CPU, Full GC, Metaspace OOM",
    "root_cause": "Insufficient MaxMetaspaceSize",
    "tags": "jvm,gc,cpu,metaspace,order-service"
}

def seed():
    print("Seeding Knowledge Base...")
    success = knowledge_service.add_insight(content=CONTENT, metadata=METADATA)
    if success:
        print("✅ Success: Insight added.")
    else:
        print("❌ Failure: Could not add insight.")

if __name__ == "__main__":
    seed()
