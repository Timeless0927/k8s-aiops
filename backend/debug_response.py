import requests
import json

try:
    resp = requests.post('http://127.0.0.1:8000/api/v1/patrol/run').json()
    diagnosis = resp['data']['checks'][1]['data']
    issues = diagnosis.get('issues', [])
    if not issues:
        print("No issues found.")
    for issue in issues:
        if issue.get('error'):
            print(f"Pod: {issue['pod']}\nError: {issue.get('error')}")
        else:
            analysis = issue.get('analysis', {})
            print(f"Pod: {issue['pod']}\nSuccess! Incident: {analysis.get('incident_type')}")
            print(f"Root Cause: {analysis.get('root_cause')}")
except Exception as e:
    print(f"Failed: {e}")
