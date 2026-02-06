import requests
import sys

try:
    print("Requesting settings WITHOUT slash...")
    # Note: allow_redirects=True is default.
    r = requests.get("http://127.0.0.1:8000/api/v1/settings")
    print(f"Status Code: {r.status_code}")
    print(f"History: {r.history}") # See if redirect happened
    if r.status_code == 200:
        print("Response OK")
    else:
        print("Error:", r.text)
except Exception as e:
    print(f"Exception: {e}")
