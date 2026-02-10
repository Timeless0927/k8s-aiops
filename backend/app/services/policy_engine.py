import logging
from app.schemas.alert import AlertmanagerPayload

logger = logging.getLogger(__name__)

class PolicyEngine:
    def evaluate(self, alert_payload: AlertmanagerPayload) -> dict | None:
        """
        Evaluate alerts and recommend an action.
        Returns: 
            dict: { "action": "restart_pod", "target": "deployment/foo", "namespace": "default" }
            None: If no action is recommended.
        """
        for alert in alert_payload.alerts:
            alert_name = alert.labels.get("alertname", "")
            namespace = alert.labels.get("namespace", "default")
            instance = alert.labels.get("instance", "")
            summary = alert.annotations.get("summary", "").lower()
            
            # Identify Target Resource (Simple heuristic for MVP)
            # Assuming instance is pod name or we need to extract from labels
            # Ideally, we should parse the workload name.
            target = f"pod/{instance}" if instance else None
            
            # Rule 1: RestartLoop in Dev
            if "RestartLoop" in alert_name or "CrashLoopBackOff" in summary:
                # Check environment (dummy check for MVP, assume dev if ns ends with -dev or default)
                # For safety in this MVP, let's restricted to 'default' namespace only
                if namespace == "default":
                    return {
                        "action": "restart_pod",
                        "target": target,
                        "namespace": namespace,
                        "reason": "Detected CrashLoopBackOff in default namespace."
                    }

            # Rule 2: DiskPressure (Tmp Cleanup)
            if "DiskPressure" in alert_name and "tmp" in summary:
                 if namespace == "default":
                    return {
                        "action": "clean_disk",
                        "target": target, # Might need node name here?
                        "namespace": namespace,
                        "reason": "Disk pressure on tmp detected."
                    }
        
        return None
