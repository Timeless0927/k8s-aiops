import requests
import sys

try:
    print("Requesting settings...")
    r = requests.get("http://127.0.0.1:8000/api/v1/settings/")
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("Response:", r.json())
    else:
        print("Error:", r.text)
except Exception as e:
    print(f"Exception: {e}")
