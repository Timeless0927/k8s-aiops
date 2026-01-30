import logging
from app.services.k8s_client import k8s_client
from app.services.prom_client import prom_client
from app.models.alert import AlertGroup

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Agent 编排器 (Core Brain)
    负责接收告警，调用工具收集信息，并最终生成诊断报告。
    """
    
    async def analyze_alert_group(self, alert_group: AlertGroup):
        """
        核心入口：分析告警组
        """
        group_key = alert_group.groupKey
        logger.info(f"开始分析告警组: {group_key}")
        
        # 1. 提取关键上下文 (Context Extraction)
        # 假设所有告警都来自同一个 Namespace/Pod (简化逻辑)
        namespace = alert_group.commonLabels.get("namespace", "default")
        pod_name = alert_group.commonLabels.get("pod")
        
        context_data = {
            "alerts": [a.labels.get("alertname") for a in alert_group.alerts],
            "namespace": namespace,
            "pod": pod_name,
            "metrics": {},
            "logs": ""
        }
        
        # 2. 收集信息 (Information Gathering)
        if pod_name:
            # 2.1 查日志
            logger.info(f"正在抓取 Pod 日志: {pod_name}")
            logs = await k8s_client.get_pod_logs(namespace, pod_name, tail_lines=50)
            context_data["logs"] = logs[:2000] # 截断防止 token 溢出
            
            # 2.2 查 CPU/Memory 使用率 (示例 PromQL)
            # 实际生产中需要生成动态 PromQL
            logger.info(f"正在查询 Metrics...")
            query = f'sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}"}}[5m]))'
            metrics = await prom_client.query(query)
            context_data["metrics"]["cpu_usage"] = metrics
            
        # 3. Analyze with LLM
        logger.info("Calling LLM for analysis...")
        analysis_result = await self._call_llm_analysis(context_data)
        context_data["analysis"] = analysis_result
        
        # Update Store (Database)
        from app.db.session import AsyncSessionLocal
        from app.db.models.alert import Alert
        from sqlalchemy import update
        
        # We need to find the specific alert record we just inserted/processed.
        # Issue: alert_store used a fingerprint or groupKey mapping. 
        # In webhook.py we inserted an Alert record. 
        # But analyze_alert_group receives a payload object, not the DB ID.
        # We might need to query by groupKey (if unique enough) or fingerprint?
        # The Alert model has 'fingerprint'. 
        
        # Strategy: Update the most recent alert with this fingerprint/group_key that has no analysis?
        # Or better: webhook.py should probably pass the DB ID to the background task (orchestrator).
        # But orchestrator signature is (alert_group: AlertGroup).
        # Let's simple query by fingerprint/raw_data matching or just latest for this group.
        # Since this is a background task immediately after insert, likelihood is high it's the latest.
        
        # Optimization: Pass fingerprint as identification.
        target_fingerprint = alert_group.commonLabels.get("alertname", "unknown")
        
        async with AsyncSessionLocal() as session:
             # Update the latest alert with this fingerprint that doesn't have analysis
             # (Or just latest one to be safe)
             # Note: This is a bit loose but works for MVP. 
             # Ideally we pass ID.
             stmt = (
                 update(Alert)
                 .where(Alert.fingerprint == target_fingerprint)
                 .where(Alert.analysis == None) # Update one pending analysis
                 # We can't easily order_by in update in generic SQL, usually need subquery.
                 # Let's select first then update.
             )
             
             # Fetch latest pending
             from sqlalchemy import select, desc
             result = await session.execute(
                 select(Alert)
                 .where(Alert.fingerprint == target_fingerprint)
                 .where(Alert.analysis == None)
                 .order_by(desc(Alert.created_at))
                 .limit(1)
             )
             record = result.scalars().first()
             
             if record:
                 record.analysis = analysis_result
                 await session.commit()
                 logger.info(f"Updated analysis for Alert ID: {record.id}")
             else:
                 logger.warning(f"No pending alert record found for fingerprint: {target_fingerprint}")
        
        logger.info(f"Analysis Complete: {analysis_result.get('summary')}")
        return context_data

    async def _call_llm_analysis(self, context: dict) -> dict:
        """
        调用 LLM 进行根因分析
        """
        import httpx
        from app.core.config import settings
        import json

        prompt = f"""
You are a Kubernetes AIOps Expert. Analyze the following alert context and provide a Root Cause Analysis (RCA) and actionable fixes.

### Context
- Namespace: {context['namespace']}
- Pod: {context['pod']}
- Alerts: {context['alerts']}
- Metrics: {context['metrics']}
- Recent Logs (Tail):
{context['logs']}

### Instructions
1. Identify the likely root cause based on logs and metrics.
2. Suggest specific `kubectl` commands or actions to fix it.
3. Output JSON format only: {{ "summary": "...", "root_cause": "...", "fix_suggestion": "..." }}
"""
        try:
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{settings.OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=60.0)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Analysis Failed: {e}")
            return {"summary": "Analysis Failed", "root_cause": str(e), "fix_suggestion": "Check logs manually"}


# 单例
orchestrator = AgentOrchestrator()
