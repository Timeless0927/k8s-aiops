from app.services.k8s_client import k8s_client

def run_kubectl(args: str) -> str:
    """
    Executes a kubectl command and returns specific output.
    """
    lines = k8s_client.execute_cli(args).split('\n')
    # Truncate if too long (simple protection)
    if len(lines) > 50:
        return "\n".join(lines[:50]) + f"\n... (Truncated {len(lines)-50} lines)"
    return "\n".join(lines)

def verify_connection() -> str:
    """
    Check if the Agent is currently connected to the Kubernetes Cluster.
    """
    status = k8s_client.check_connection()
    if status["connected"]:
        return "✅ Connected to Kubernetes Cluster (API Reachable)."
    else:
        return f"❌ Disconnected from Cluster. Error: {status['error']}"
