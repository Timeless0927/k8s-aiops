import os

log_file = "alert_debug.log"
if not os.path.exists(log_file):
    print("backend.log not found.")
else:
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            print("".join(lines[-50:]))
    except Exception as e:
        print(f"Error reading log: {e}")
