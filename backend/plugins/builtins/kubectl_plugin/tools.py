from app.services.k8s_client import k8s_client

from app.services.log_forensics import LogForensicsService

def run_kubectl(args: str, auto_analyze: bool = False) -> str:
    """
    Executes a kubectl command.
    - args: The kubectl command arguments (e.g., "logs my-pod", "get pods").
    - auto_analyze: Set to Valid ONLY if you are fetching 'logs' or 'describe'. It will return AI analysis of the error.
    """
    output = k8s_client.execute_cli(args)
    
    # 1. Standard Truncation
    lines = output.split('\n')
    truncated_output = "\n".join(lines[:50]) + (f"\n... (Truncated {len(lines)-50} lines)" if len(lines) > 50 else "")
    
    # 2. Smart Analysis (Token Optimization)
    analysis_text = ""
    if auto_analyze and ("logs" in args or "describe" in args):
        # We use the FULL output for analysis, not truncated
        structured, _ = LogForensicsService.analyze_logs(output)
        if structured:
             analysis_text = f"""
🧠 **Smart Analysis (Auto-Generated)**:
- **Incident**: {structured.get('incident_type')}
- **Cause**: {structured.get('root_cause')}
- **Fix**: {structured.get('suggestion')}
"""
    
    return truncated_output + analysis_text

def verify_connection() -> str:
    """
    Check if the Agent is currently connected to the Kubernetes Cluster.
    """
    status = k8s_client.check_connection()
    if status["connected"]:
        return "✅ Connected to Kubernetes Cluster (API Reachable)."
    else:
        return f"❌ Disconnected from Cluster. Error: {status['error']}"
