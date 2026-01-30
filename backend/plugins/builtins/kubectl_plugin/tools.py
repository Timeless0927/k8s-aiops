from app.services.k8s_client import k8s_client

def run_kubectl(args: str) -> str:
    """
    Executes a kubectl command and returns specific output.
    """
    return k8s_client.execute_cli(args)
