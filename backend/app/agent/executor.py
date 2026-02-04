import json
import logging
from app.db.session import AsyncSessionLocal
from app.services.chat_history import ChatHistoryService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def run_agent_graph(websocket, conversation_id: str, last_user_message: str, session: AsyncSession = None, conversation_type: str = "chat"):
    """
    Executes the LangGraph agent and streams results to WebSocket.
    Uses provided session or creates a new one.
    """
    from app.agent.graph.graph import graph
    
    # helper for session management
    class SessionContext:
        def __init__(self, provided_session):
            self.provided = provided_session
            self.local = None
        
        async def __aenter__(self):
            if self.provided:
                return self.provided
            self.local = AsyncSessionLocal()
            return await self.local.__aenter__()
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.local:
                await self.local.__aexit__(exc_type, exc_val, exc_tb)

    async with SessionContext(session) as db_session:
        # Load messages (optional check)
        # db_messages = await ChatHistoryService.get_recent_messages(db_session, conversation_id, limit=20)
        
        # Build Inputs
        # NOTE: For now we trust graph state management or start fresh?
        # Ideally we load from DB.
        db_messages = await ChatHistoryService.get_recent_messages(db_session, conversation_id, limit=20)
        
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
        
        initial_messages = []
        
        # Inject Dynamic System Prompt
        from app.services.plugin_manager import plugin_manager
        active_plugins = plugin_manager.get_active_plugins()
        
        # Build Capabilities with Tool Names
        caps = []
        for name, data in active_plugins.items():
            # Get tools for this plugin? 
            # PluginManager doesn't easily map Plugin -> Tool Names in metadata. 
            # We can infer or just list description.
            # Ideally we check tools_registry but that is flat.
            # Simplified: Just trust description OR if builtin known tools.
            desc = data.get('description', 'Enabled')
            if name == "kubectl_plugin":
                desc += " (Tools: run_kubectl)"
            elif name == "k8sgpt_plugin":
                desc += " (Tools: run_k8sgpt)"
            
            caps.append(f"- {name}: {desc}")
            
        capabilities_text = "\n".join(caps)
        
        # Dynamic Rules Construction
        rules = [
            "1. FACTUALITY: Do NOT invent, guess, or hallucinate labels.",
            "2. UNAVAILABLE TOOLS: If a requested tool is NOT listed in ENABLED CAPABILITIES (or its tools), explicitly state it is unavailable. DO NOT FABRICATE outputs.",
             "3. SYNTAX: Use correct JSON/YAML flags for kubectl.",
             "4. RESPONSE FIRST: When using a tool (especially k8sgpt or scanners), ALWAYS start your response with a short sentence confirming the action (e.g., 'I will scan the default namespace now...') BEFORE calling the tool. Do NOT stay silent."
        ]

        if "kubectl_plugin" in active_plugins:
            rules.append("4. EVIDENCE: Run `run_kubectl` to verify facts.")
        
        if "k8sgpt_plugin" in active_plugins:
            rules.append("5. DIAGNOSTICS: Use `run_k8sgpt` for health checks if available.")

        if "prometheus_plugin" in active_plugins:
             rules.append("6. METRICS: Use `run_prometheus_query` to answer performance questions (CPU, Memory, Rate).")
             rules.append("7. PROMQL: Examples: `sum(rate(container_cpu_usage_seconds_total[5m]))` (CPU), `sum(container_memory_usage_bytes)` (Memory).")
        
        if "loki_plugin" in active_plugins:
             rules.append("8. LOGS: Use `run_loki_query` to answer troubleshooting questions about errors or exceptions.")
             rules.append("9. LOGQL: Examples: `{namespace=~'.+'}` (all), `{app='foo'} |= 'error'`.")
        
        if "knowledge_plugin" in active_plugins:
             rules.append("10. MEMORY: Before answering complex issues, ALWAYS use `search_knowledge`.")
             rules.append("11. LEARNING: If the user TEACHES you a solution or CONFIRMS a fix, you MUST use `save_insight` to record it. Don't wait for permission.")

        rules_text = "\n".join(rules)

        system_content = f"""You are a Kubernetes AIOps Agent specialized in troubleshooting.
## ENABLED CAPABILITIES:
{capabilities_text}

## CRITICAL RULES:
{rules_text}
"""
        initial_messages.append(SystemMessage(content=system_content))
        
        for msg in db_messages:
            if msg.role == "user":
                initial_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                if not msg.content: msg.content = ""
                initial_messages.append(AIMessage(content=msg.content))
            elif msg.role == "tool":
                call_id = getattr(msg, "tool_call_id", "unknown") 
                initial_messages.append(ToolMessage(tool_call_id=call_id, content=msg.content, name="unknown"))
        
        # New User Message (Append and Persist)
        if last_user_message:
            # 1. Start with in-memory append
            initial_messages.append(HumanMessage(content=last_user_message))
            
            # 2. Persist to DB
            try:
                # Ensure conversation exists first!
                await ChatHistoryService.ensure_conversation(db_session, conversation_id, conversation_type)
                await ChatHistoryService.add_message(db_session, conversation_id, "user", last_user_message)
            except Exception as e:
                logger.error(f"Failed to save user prompt: {e}")
        
        inputs = {"messages": initial_messages}
        
        logger.info(f"Starting Graph Execution for Conversation {conversation_id}")
        
        async for event in graph.astream_events(inputs, version="v1"):
            kind = event["event"]
            name = event["name"]
            data = event["data"]
            
            # 1. Token Stream
            if kind == "on_chat_model_stream":
                chunk = data.get("chunk")
                if chunk and chunk.content:
                    await websocket.send_json({"type": "token", "content": chunk.content})
            
            # 2. Assistant Message Complete
            elif kind == "on_chat_model_end":
                output = data.get("output")
                
                # Check for AIMessage (relaxed check)
                content = ""
                is_valid_msg = False
                
                if hasattr(output, "content") and output.content:
                    content = output.content
                    is_valid_msg = True
                elif isinstance(output, str):
                    content = output
                    is_valid_msg = True
                
                if is_valid_msg and content:
                     try:
                        saved_msg = await ChatHistoryService.add_message(db_session, conversation_id, "assistant", content)
                     except Exception as e:
                        logger.error(f"Persist Fail: {e}")
                
                # Notify Tool Starts
                if hasattr(output, "tool_calls") and output.tool_calls:
                    for tc in output.tool_calls:
                        await websocket.send_json({
                            "type": "tool_start",
                            "tool": tc["name"],
                            "args": json.dumps(tc["args"]) 
                        })

            # 3. Agent Node Complete (Failsafe)
            elif kind == "on_chain_end" and name == "agent":
                node_output = data.get("output")
                if node_output and "messages" in node_output:
                    for msg in node_output["messages"]:
                        # Check for AIMessage (relaxed check)
                        if hasattr(msg, "content") and msg.content and getattr(msg, "type", "") == "ai":
                             try:
                                # Deduplicate? ChatHistoryService logic helps?
                                # Ideally we rely on ID, but we generate new ID.
                                # Simple check: Was the last message same content?
                                # For now, just append.
                                await ChatHistoryService.add_message(db_session, conversation_id, "assistant", msg.content)
                             except Exception as e:
                                pass

            # 4. Tool Execution Complete
            elif kind == "on_chain_end" and name == "tools":
                node_output = data.get("output")
                if node_output and "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, ToolMessage):
                            await websocket.send_json({
                                "type": "tool_result",
                                "output": msg.content
                            })
                            
                            try:
                                await ChatHistoryService.add_message(
                                    db_session, 
                                    conversation_id, 
                                    "tool", 
                                    msg.content,
                                    tool_call_id=msg.tool_call_id
                                )
                            except Exception as e:
                                pass
            
        await websocket.send_json({"type": "done"})
