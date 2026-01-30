import subprocess
import os
from app.core.config import settings

def run_k8sgpt(namespace: str = None, filters: str = None, anonymize: bool = False) -> str:
    """
    Runs k8sgpt analyze to scan the cluster for issues.
    Args:
        namespace: Optional, specific namespace(s) to scan.
        filters: Optional, comma separated filters (e.g. "Pod,Service").
        anonymize: Whether to anonymize sensitive data (default False).
    """
    try:
        # Determine kubeconfig path from Settings (loaded from .env)
        kubeconfig_path = settings.KUBECONFIG or r"C:\Users\issuser\.kube\config"
        
        # Base Command
        cmd = ["k8sgpt", "analyze", "--output", "json", "--explain=false", "--kubeconfig", kubeconfig_path]
        
        # Add Optional Args
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        if filters:
            cmd.extend(["--filter", filters])
            
        if anonymize:
            cmd.append("--anonymize")
        
        # Check if k8sgpt.exe exists in current dir (backend root)
        if os.path.exists("k8sgpt.exe"):
             cmd[0] = os.path.abspath("k8sgpt.exe")
        
        # Suppress Ollama error by setting dummy env if not set
        env = os.environ.copy()
        if "OLLAMA_RUNNERS_DIR" not in env:
            import tempfile
            env["OLLAMA_RUNNERS_DIR"] = tempfile.gettempdir()

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
        
        # K8SGPT writes logs to stderr even on success sometimes, or "llm runner" error.
        # Check if we got valid JSON in stdout first.
        if result.stdout and result.stdout.strip().startswith("{"):
            return result.stdout
            
        if result.returncode != 0:
            # Check for common connection errors
            if "refused" in result.stderr.lower() or "unable to connect" in result.stderr.lower():
                 return "Error: Unable to connect to Kubernetes Cluster. Please check if your cluster is running and kubeconfig is valid."
            
            return f"Error running k8sgpt: {result.stderr}"
            
        return result.stdout
    except Exception as e:
        return f"failed to run k8sgpt: {str(e)}"
