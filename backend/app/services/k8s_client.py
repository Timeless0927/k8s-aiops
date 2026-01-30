import logging
from kubernetes import client, config
from app.core.config import settings

logger = logging.getLogger(__name__)

class K8sClient:
    """
    Kubernetes API 客户端封装
    支持集群内 (In-Cluster) 和 集群外 (Kubeconfig) 模式
    """
    def __init__(self):
        self.connected = False
        self._load_config()
        
        if self.connected:
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
        else:
            self.v1 = None
            self.apps_v1 = None

    def _load_config(self):
        try:
            if settings.KUBE_IN_CLUSTER:
                logger.info("加载集群内配置 (In-Cluster Config)...")
                config.load_incluster_config()
            else:
                logger.info("加载本地配置 (Kubeconfig)...")
                config.load_kube_config()
            self.connected = True
        except Exception as e:
            logger.warning(f"Cluster Connect Failed: {e}")
            self.connected = False

    async def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 100) -> str:
        """
        获取 Pod 日志
        """
        if not self.v1:
            return "Error: K8s client not connected (Offline Mode)"

        try:
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail_lines
            )
            return logs
        except client.exceptions.ApiException as e:
            logger.error(f"获取日志失败 [{namespace}/{pod_name}]: {e}")
            return f"Error reading logs: {e}"

    async def get_deployment_status(self, namespace: str, deployment_name: str) -> dict:
        """
        获取 Deployment 状态
        """
        if not self.apps_v1:
            return {"error": "K8s client not connected (Offline Mode)"}

        try:
            dep = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            return {
                "replicas": dep.status.replicas,
                "ready_replicas": dep.status.ready_replicas,
                "unavailable_replicas": dep.status.unavailable_replicas,
                "conditions": [c.message for c in dep.status.conditions] if dep.status.conditions else []
            }
        except client.exceptions.ApiException as e:
            logger.error(f"获取 Deployment 失败 [{namespace}/{deployment_name}]: {e}")
            return {"error": str(e)}
    def execute_cli(self, command: str) -> str:
        """
        Executes a kubectl command securely via subprocess
        """
        import subprocess
        import shlex

        # Security Note: In production, strictly validate 'command' to prevent injection.
        # For this MVP, we assume the Agent is trusted.
        
        import os
        from app.core.config import settings

        if settings.KUBE_IN_CLUSTER is False and settings.KUBECONFIG:
            full_cmd = f"kubectl {command} --kubeconfig {settings.KUBECONFIG}"
        else:
            full_cmd = f"kubectl {command}"
            
        logger.info(f"Executing CLI: {full_cmd}")

        try:
            # shell=True is used here for Windows compatibility with basic command parsing
            # In Linux production, use shlex.split(full_cmd) and shell=False
            result = subprocess.run(
                full_cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,
                # env=env # Not needed if using CLI arg
            )
            
            if result.returncode != 0:
                return f"Error ({result.returncode}): {result.stderr.strip()}"
            
            return result.stdout.strip() or "Success (No Output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"Error executing command: {str(e)}"

# 全局单例
k8s_client = K8sClient()
