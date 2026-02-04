import json
import logging

logger = logging.getLogger(__name__)

def run_kubectl_mock(args: str) -> str:
    """
    Simulates kubectl output for demo purposes.
    """
    logger.info(f"🎭 Mock Kubectl Executing: {args}")
    
    args = args.strip()
    
    # 1. Get Pods
    if "get pods" in args:
        if "-o json" in args:
            return json.dumps({
                "apiVersion": "v1",
                "items": [
                    {
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {
                            "name": "pod-123",
                            "namespace": "default",
                            "labels": {"app": "demo-app"}
                        },
                        "status": {
                            "phase": "Running",
                            "containerStatuses": [
                                {
                                    "name": "main",
                                    "ready": True,
                                    "restartCount": 5,
                                    "state": {
                                        "running": {"startedAt": "2023-10-01T00:00:00Z"}
                                    }
                                }
                            ]
                        }
                    }
                ]
            })
        else:
            return """
NAME      READY   STATUS    RESTARTS   AGE
pod-123   1/1     Running   5          10h
"""

    # 2. Logs
    if "logs" in args and "pod-123" in args:
        return """
[INFO] Starting application...
[INFO] Processing request #1001
[ERROR] java.lang.OutOfMemoryError: Java heap space
    at com.example.MyService.process(MyService.java:55)
    at com.example.Worker.run(Worker.java:12)
[INFO] Shutting down...
"""

    # 3. Events / Describe
    if "events" in args or "describe" in args:
         return """
Events:
  Type     Reason     Age   From               Message
  ----     ------     ---   ----               -------
  Warning  OOMKilled  5m    kubelet            Container main was terminated by OOMKilled
  Normal   Pulling    5m    kubelet            Pulling image "demo:latest"
  Normal   Created    4m    kubelet            Created container main
"""

    # Default
    return f"Mock Kubectl: resource '{args}' not found."
