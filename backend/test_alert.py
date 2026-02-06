import requests
import json

url = "http://localhost:8000/api/v1/webhook/alertmanager"
payload = {
    "receiver": "webhook",
    "status": "firing",
    "alerts": [
        {
            "status": "firing",
            "labels": {
                "alertname": "JVM_GC_Overhead",
                "severity": "critical",
                "instance": "order-service-pod-x",
                "namespace": "payment"
            },
            "annotations": {
                "summary": "High CPU and Frequent Full GC",
                "description": "Pod is spending >98% time in GC. Old Gen usage is high."
            }
        }
    ],
    "groupLabels": {"alertname": "JVM_GC_Overhead"},
    "commonLabels": {"severity": "critical"},
    "commonAnnotations": {},
    "externalURL": "http://alertmanager",
    "version": "4",
    "groupKey": "{}:{alertname=\"JVM_GC_Overhead\"}"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
