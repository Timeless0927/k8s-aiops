import os
import multiprocessing

# Gunicorn configuration file
# Reference: https://docs.gunicorn.org/en/stable/settings.html

# Bind
bind = "0.0.0.0:8000"

# Worker Options
# Workers: (2 x CPUs) + 1 is the standard formula
# For K8s, we often set this based on the Limit, but 4 is a safe default for 500m-1000m limits
workers = int(os.getenv("GUNICORN_WORKERS", "4"))

# Worker Class
# Uvicorn's worker class for ASGI
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout
# Increase timeout for slow LLM responses if necessary
timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # Stdout
errorlog = "-"   # Stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Process Name
proc_name = "k8s_aiops_backend"
