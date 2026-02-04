import asyncio
import logging
from app.schemas.alert import AlertmanagerPayload

logger = logging.getLogger(__name__)

class AlertQueueService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlertQueueService, cls).__new__(cls)
            cls._instance.queue = asyncio.Queue()
            cls._instance.is_running = False
            
            # Setup Debug Logging
            fh = logging.FileHandler("alert_debug.log", mode='a', encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            logger.addHandler(fh)
            logger.setLevel(logging.INFO)
            
        return cls._instance

    async def enqueue(self, payload: AlertmanagerPayload):
        """Push an alert payload to the processing queue."""
        await self.queue.put(payload)
        logger.info(f"Alert enqueued. Current queue size: {self.queue.qsize()}")

    async def process_queue(self):
        """Background worker to process alerts."""
        self.is_running = True
        logger.info("AlertQueueService worker started.")
        
        while self.is_running:
            try:
                # Wait for an item from the queue
                payload = await self.queue.get()
                
                # Mock Processing Logic (MVP)
                await self._process_payload(payload)
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
                await asyncio.sleep(1) # Prevent tight loop on error

    async def _process_payload(self, payload: AlertmanagerPayload):
        """
        Core logic for handling the alert:
        1. Parse Alert
        2. Construct Prompt
        3. Trigger Agent (via GraphExecutor)
        """
        from app.agent.executor import run_agent_graph
        import uuid
        
        for alert in payload.alerts:
            # 1. Parse Basic Info
            alert_name = alert.labels.get('alertname', 'Unknown Alert')
            severity = alert.labels.get('severity', 'info')
            summary = alert.annotations.get('summary', 'No summary provided')
            description = alert.annotations.get('description', '')
            instance = alert.labels.get('instance', 'unknown-instance')
            namespace = alert.labels.get('namespace', 'default') # Assumption
            
            logger.info(f"⚡ PROCESSING ALERT: [{severity.upper()}] {alert_name} - {summary}")
            
            # 2. Construct Investigation Prompt
            # 2. Construct Intelligent Prompt (Goal-Based)
            
            # A. Dynamic Context Hints
            hints = []
            lower_summary = summary.lower()
            if "cpu" in lower_summary:
                hints.append("重点检查 CPU 使用率 (Metrics) 和 Top 消耗进程。")
            elif "memory" in lower_summary or "oom" in lower_summary:
                hints.append("怀疑是内存泄漏或 OOMKilled，请检查 Events 和 上一次重启的原因。")
            elif "network" in lower_summary or "timeout" in lower_summary:
                hints.append("怀疑是网络问题，请检查 Endpoints 和 Service 状态。")
            
            if severity == "critical":
                hints.append("这是一个严重告警，请优先确认服务可用性。")
            
            hint_text = "\n".join([f"- {h}" for h in hints]) if hints else "- 无特定线索，请按标准流程排查。"

            prompt = f"""
🚨 **收到告警 (ALERT RECEIVED)**
- **名称**: {alert_name}
- **级别**: {severity}
- **实例**: {instance}
- **摘要**: {summary}
- **描述**: {description}

---
**你的任务 (Mission)**:
你是一名资深 SRE 专家。你的目标是**自主**查明 `{instance}` 发生 `{alert_name}` 的根本原因，并给出修复建议。

**约束 (Constraints)**:
1. **Scope (智能边界)**: 聚焦于 `{instance}`。
    - 如果 Pod 存在，仅排查该 Pod。
    - **关键**: 如果 Pod 已销毁/不存在，**允许**查找其所属的 Controller (Deployment/StatefulSet) 或同名的新 Pod。
    - **严禁**: 严禁扫描其他 Namespace，严禁排查与该应用无关的资源。
2. **Tools**: 自行决定使用哪些工具 (LogQL, Kubectl, PromQL 等)。
3. **Language**: 必须使用中文回答。
4. **Memory (自我进化)**: 查明原因后，**必须**调用 `save_insight`。参数要求：
    - `topic`: 简短概括 (如 "Fix OOM for App X")
    - `content`: 详细修复步骤
    - `symptoms`: 现象 (如 "CPU > 400%")
    - `root_cause`: 根因
    - `tags`: 标签列表 (如 ["cpu", "java", "oom"])

**上下文暗示 (Hints)**:
{hint_text}

(注意：如果这是 'TestAlert'，这是一个单点测试。)

**执行流程 (Execution Protocol)**:
1. **第一步 (强制)**: 必须先调用 `search_knowledge` 工具，查询 `{alert_name}` 和 `{instance}` 是否有历史解决方案。
    - 如果找到匹配的“已知问题”或“正常现象”，**请直接引用结论并结束**，无需进行后续排查。
2. **第二步**: 如果知识库无记录，则再使用 `kubectl` 或 `promql` 进行排查。

现在，请开始行动。
"""
            
            # 3. Create Ephemeral Conversation ID
            conversation_id = f"alert-{uuid.uuid4()}"
            
            # 4. Mock WebSocket for Background Execution
            class MockWebSocket:
                async def send_json(self, data):
                    # In future, this connects to Notifier (DingTalk/Feishu)
                    # For now, just log interesting events
                    msg_type = data.get("type")
                    if msg_type == "tool_start":
                        logger.info(f"🤖 Agent Tool: {data.get('tool')} ({data.get('args')})")
                    elif msg_type == "tool_result":
                        logger.info(f"🔧 Tool Output: {data.get('output')[:100]}...") # Truncate
                    elif msg_type == "token":
                        pass # Ignore tokens
            
            mock_ws = MockWebSocket()
            
            try:
                # 4. Persist Alert to DB (New)
                from app.db.session import AsyncSessionLocal
                from app.db.models.alert import Alert
                
                async with AsyncSessionLocal() as db:
                    new_alert = Alert(
                        id=conversation_id,
                        fingerprint=None, # Simplify for MVP
                        title=alert_name,
                        severity=severity,
                        status="active",
                        source=instance,
                        summary=summary,
                        conversation_id=conversation_id
                    )
                    db.add(new_alert)
                    await db.commit()
                    logger.info(f"💾 Alert persisted to DB: {conversation_id}")

                # 5. Run Agent
                logger.info(f"🚀 Triggering Agent Investigation for {conversation_id}")
                
                result = await run_agent_graph(
                    websocket=mock_ws,
                    conversation_id=conversation_id,
                    last_user_message=prompt,
                    session=None,
                    conversation_type="alert"
                )
                logger.info(f"✅ Investigation Complete for {conversation_id}")

                # 6. Notify (DingTalk)
                from app.services.notifier import notifier
                
                report = f"""## 🚨 故障告警: {alert_name}
**来源**: {instance}
**级别**: {severity.upper()}
**概要**: {summary}

---
### 🤖 AI 侦探调查报告
(Conversation ID: {conversation_id})

✅ 调查已完成。由于篇幅限制，请点击下方链接查看完整诊断过程与建议。

> [查看详情](http://localhost:5173/chat?id={conversation_id})
"""
                await notifier.send_markdown(f"故障告警: {alert_name}", report)
                
            except Exception as e:
                logger.error(f"❌ Agent Investigation Failed: {e}")
                # Notify Failure
                from app.services.notifier import notifier
                await notifier.send_markdown(f"告警处理失败: {alert_name}", f"Agent execution failed: {str(e)}\n\n(ID: {conversation_id})")
