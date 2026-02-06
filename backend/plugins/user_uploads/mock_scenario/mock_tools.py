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
                                    "restartCount": 0,
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
pod-123   1/1     Running   0          10h
"""

    # 2. Top (CPU Usage) - High CPU Scenario
    if "top" in args:
        return """
NAME                  CPU(cores)   MEMORY(bytes)
pod-123               950m         512Mi
order-service-pod-x   2100m        1024Mi
"""

    # JVM GC Scenario
    if "logs" in args and "order-service" in args:
        return """
2023-10-27T10:00:01.234 [GC (Allocation Failure) [PSYoungGen: 65536K->1024K(76800K)] 65536K->66000K(251904K), 0.0456789 secs]
2023-10-27T10:00:01.300 [Full GC (Ergonomics) [PSYoungGen: 1024K->0K(76800K)] [ParOldGen: 65000K->240000K(450000K)] 241024K->240000K(526800K), [Metaspace: 250000K->250000K(1048576K)], 1.5432109 secs]
[WARN] GC overhead limit exceeded
[ERROR] java.lang.OutOfMemoryError: Metaspace
"""
    
    # Logs - High CPU Loop (Existing)
    if "logs" in args and "pod-123" in args:
        return """
[INFO] Starting high-performance calculation...
[INFO] Loading large dataset...
[WARN] Thread-5 consuming 99% CPU
[WARN] Thread-6 consuming 98% CPU
[INFO] Processing batch 10592...
"""

    # 4. Events / Describe
    if "events" in args or "describe" in args:
         return """
Events:
  Type     Reason     Age   From               Message
  ----     ------     ---   ----               -------
  Normal   Scheduled  10h   default-scheduler  Successfully assigned default/pod-123 to node-1
  Normal   Pulling    10h   kubelet            Pulling image "demo:latest"
  Normal   Created    10h   kubelet            Created container main
  Normal   Started    10h   kubelet            Started container main
"""

    # 5. Get Nodes (Basic)
    if "get nodes" in args:
        return """
NAME       STATUS   ROLES           AGE   VERSION
node-1     Ready    control-plane   10d   v1.28.0
node-2     Ready    worker          10d   v1.28.0
"""

    # Default
    return f"Mock Kubectl: resource '{args}' not found."
