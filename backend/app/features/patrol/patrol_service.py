import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List
# Re-import checks (Assuming simple checks were deleted, I need to recreate them or inline simplified versions)
# The user deleted checks/*.py, so I will inline simplified logic or recreate them quickly.
from app.services.k8s_client import k8s_client
from app.services.log_forensics import LogForensicsService

logger = logging.getLogger(__name__)

class PatrolService:
    def __init__(self):
        self.report_cache = {} # In-memory cache for HTML reports (ID -> HTML)

    async def run_patrol(self) -> Dict[str, Any]:
        logger.info("Running Patrol 2.0...")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "checks": []
        }

        try:
            # 1. Health Check (Simplified Inline)
            health_data = await self._check_health()
            report_data["checks"].append({"name": "Cluster Health", "data": health_data})

            # 2. Diagnosis with Log Forensics
            diag_data = await self._diagnose_logs()
            report_data["checks"].append({"name": "AI Diagnosis", "data": diag_data})
            
            if diag_data.get("issues"):
                report_data["status"] = "warning"

        except Exception as e:
            logger.error(f"Patrol failed: {e}")
            report_data["status"] = "failed"
            report_data["error"] = str(e)

        # Generate Markdown
        markdown = self._generate_markdown(report_data)

        return {
            "data": report_data,
            "markdown": markdown
        }

    async def _check_health(self):
        if not k8s_client.connected: return {"status": "error", "message": "K8s Disconnected"}
        v1 = k8s_client.v1
        try:
            nodes = v1.list_node().items
            not_ready = [n.metadata.name for n in nodes if not any(c.status == "True" and c.type == "Ready" for c in n.status.conditions)]
            return {"status": "healthy" if not not_ready else "warning", "not_ready_nodes": not_ready}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _diagnose_logs(self):
        """
        New Logic: Identify candidates and dispatch Agent tasks.
        """
        issues = []
        if not k8s_client.connected: return {"issues": []}
        
        # Find CrashLoopBackOff - This part identifies "Targets"
        try:
            pods = k8s_client.v1.list_pod_for_all_namespaces(limit=50).items
            for pod in pods:
                if not pod.status.container_statuses: continue
                
                for cs in pod.status.container_statuses:
                    if (cs.state.waiting and cs.state.waiting.reason == "CrashLoopBackOff") or (cs.restart_count > 5):
                        
                        # TRIGGER AGENT
                        await self._dispatch_agent_investigation(pod, cs)

                        issues.append({
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "status": "Investigation Triggered"
                        })
        except Exception as e:
            logger.error(f"Diagnosis triggering failed: {e}")
            
        return {"issues": issues}

    async def _dispatch_agent_investigation(self, pod, container_status):
        from app.agent.executor import run_agent_graph
        import uuid
        from app.services.connection_manager import manager as connection_manager

        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        container = container_status.name
        reason = container_status.state.waiting.reason if container_status.state.waiting else "High Restarts"

        conversation_id = f"patrol-{uuid.uuid4()}"
        logger.info(f"👮 Patrol dispatching investigation: {conversation_id} for {pod_name}")

        prompt = f"""
🚨 **主动巡检发现异常 (PATROL ALERT)**
- **Pod**: {pod_name}
- **Namespace**: {namespace}
- **Container**: {container}
- **Reason**: {reason}

---
**你的任务**:
作为 SRE，请深入调查这个 Pod 的问题。
1. **查阅日志**: 获取该 Pod 的日志。
2. **AI 分析**: 你的工具会自动分析日志并告诉你根因 (Smart Tool)。
3. **沉淀知识**: 查明原因后，调用 `save_insight` 保存结论。
"""
        # Mock WebSocket for Background Execution
        class MockWebSocket:
            async def send_json(self, data):
                await connection_manager.broadcast_json(conversation_id, data)

        try:
            # Fire and Forget (Background Task)
            asyncio.create_task(run_agent_graph(
                websocket=MockWebSocket(),
                conversation_id=conversation_id,
                last_user_message=prompt,
                session=None,
                conversation_type="patrol"
            ))
        except Exception as e:
            logger.error(f"Failed to dispatch agent: {e}")

    def _generate_markdown(self, data):
        # Simplified Report - just showing triggers
        md = f"# 🛡️ Patrol Report 2.0\nTime: {data['timestamp']}\n\n"
        h = data['checks'][0]['data']
        md += f"## Cluster Health: {h['status'].upper()}\n"
        
        diag = data['checks'][1]['data']
        md += f"\n## 🧠 AI Diagnosis Triggered\n"
        if not diag['issues']:
            md += "✅ No anomalies detected.\n"
        else:
            for i in diag['issues']:
                md += f"- **Target**: {i['pod']} ({i['namespace']})\n"
                md += f"  - Status: *Agent Investigation Started*\n"
        return md

patrol_service = PatrolService()
