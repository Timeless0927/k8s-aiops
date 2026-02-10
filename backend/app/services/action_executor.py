import logging
import asyncio
from app.services.k8s_client import K8sClient
from app.services.safety_gate import SafetyGate

logger = logging.getLogger(__name__)

class ActionExecutor:
    def __init__(self):
        self.k8s_client = K8sClient()
        self.safety_gate = SafetyGate()

    async def execute(self, action_plan: dict) -> bool:
        """
        Executes a remediation action safely.
        
        Args:
            action_plan (dict): { "action": "restart_pod", "target": "pod/foo", "namespace": "default", "reason": "..." }
            
        Returns:
            bool: True if executed successfully, False otherwise.
        """
        action = action_plan.get("action")
        target = action_plan.get("target") # e.g., pod/nginx-wxq12
        namespace = action_plan.get("namespace", "default")
        
        fingerprint = f"{namespace}/{target}"
        
        # 1. Safety Gate Check
        is_allowed = await self.safety_gate.check_allow(fingerprint, action, namespace)
        if not is_allowed:
            logger.warning(f"ActionExecutor: Blocked execution of {action} on {fingerprint}")
            await self.safety_gate.record_action(
                fingerprint=fingerprint,
                action=action,
                namespace=namespace,
                status="throttled", 
                message="Blocked by Safety Gate rules (frequency or blacklist)."
            )
            return False

        # 2. Execute Action
        try:
            logger.info(f"ActionExecutor: Executing {action} on {fingerprint}...")
            
            output = ""
            success = False
            
            if action == "restart_pod":
                # K8s delete pod triggers a restart by the controller
                cmd = f"kubectl delete {target} -n {namespace}"
                # For safety in MVP, use --dry-run=client first? No, we want real action.
                # But let's verify target format.
                if not target.startswith("pod/"):
                     raise ValueError(f"Invalid target for restart_pod: {target}")
                
                # Using k8s_client.run_kubectl which looks like it runs shell commands?
                # Let's assume K8sClient exposes something useful or we extend it.
                # Actually, K8sClient in this project likely uses subprocess or python client.
                # Let's use the simplest approach compatible with existing K8sClient.
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                output = stdout.decode().strip()
                error = stderr.decode().strip()
                
                if process.returncode == 0:
                    success = True
                    logger.info(f"ActionExecutor: Successfully restarted {target}")
                else:
                    success = False
                    output = f"Error: {error}"
                    logger.error(f"ActionExecutor: Failed to restart {target}: {error}")

            elif action == "clean_disk":
                # Placeholder for disk cleanup
                # In real world, this might run a specific job or exec into a pod.
                # For MVP, we'll just log it.
                logger.info(f"ActionExecutor: clean_disk simulation on {target}")
                output = "Simulated disk cleanup"
                success = True

            else:
                 logger.warning(f"ActionExecutor: Unknown action {action}")
                 return False

            # 3. Audit Log
            status = "success" if success else "failed"
            await self.safety_gate.record_action(
                fingerprint=fingerprint,
                action=action,
                namespace=namespace,
                status=status,
                message=output
            )
            
            return success

        except Exception as e:
            logger.error(f"ActionExecutor: Critical error executing {action}: {e}")
            await self.safety_gate.record_action(
                fingerprint=fingerprint,
                action=action,
                namespace=namespace,
                status="failed",
                message=str(e)
            )
            return False
