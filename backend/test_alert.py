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
                "alertname": "TestAlert",
                "severity": "critical",
                "instance": "pod-123"
            },
            "annotations": {
                "summary": "High CPU Usage",
                "description": "CPU usage is above 90%"
            }
        }
    ],
    "groupLabels": {"alertname": "TestAlert"},
    "commonLabels": {"severity": "critical"},
    "commonAnnotations": {},
    "externalURL": "http://alertmanager",
    "version": "4",
    "groupKey": "{}:{alertname=\"TestAlert\"}"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
