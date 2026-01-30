import json
import asyncio
from typing import List, cast
from langchain_core.messages import ToolMessage, AIMessage
from app.agent.graph.state import AgentState
from app.services.plugin_manager import plugin_manager

async def tool_node(state: AgentState):
    """
    Executes tool calls from the last AI message.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Ensure last message is an AIMessage with tool_calls
    # Note: In LangGraph, we typically route here only if tool_calls exist.
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}
    
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        arguments = tool_call["args"] # LangChain parses this to dict automatically
        call_id = tool_call["id"]
        
        handler = plugin_manager.get_tool_handler(tool_name)
        
        result_content = ""
        
        if handler:
            # SAFETY GUARD: Human-in-the-loop Approval
            is_blocked = False
            block_reason = ""
            
            # Check sensitive operations (Only for kubectl for now)
            if tool_name == "run_kubectl":
                 # Extract command verbs
                 # Note: "args" is the parameter name in kubectl_plugin
                 raw_args = arguments.get("args", "")
                 if isinstance(raw_args, str):
                     cmd_args = raw_args.lower().split()
                 else:
                     # Fallback if somehow list
                     cmd_args = []
                 
                 sensitive_verbs = ["delete", "restart", "scale", "edit", "patch", "cordon", "drain", "apply"]
                 
                 # Check if any sensitive verb is in the command arguments
                 if any(verb in cmd_args for verb in sensitive_verbs):
                     # Check User Consent
                     # We need to find the last HUMAN message.
                     # Messages list: [System, Human, AI, Human, AI(tool_call)] -> We want last Human
                     last_human_msg = None
                     for m in reversed(messages[:-1]): # Exclude the current AI tool call msg
                         if m.type == "human":
                             last_human_msg = m
                             break
                     
                     consent_keywords = ["confirm", "yes", "proceed", "ok", "approve", "go ahead"]
                     user_text = last_human_msg.content.lower() if last_human_msg else ""
                     
                     # Simple keyword check
                     has_consent = any(kw in user_text for kw in consent_keywords)
                     
                     if not has_consent:
                         is_blocked = True
                         block_reason = f"⚠️ SAFETY BLOCK: Operation '{' '.join(cmd_args)}' requires approval. Please ask user to reply 'confirm' or 'yes'."

            try:
                if is_blocked:
                    result_content = block_reason
                else:
                    # Execute handler
                    if asyncio.iscoroutinefunction(handler):
                        result_content = await handler(**arguments)
                    else:
                        result_content = handler(**arguments)
                    
                # Ensure string output for LLM consumption
                if not isinstance(result_content, str):
                    # For JSON objects, dump them
                    if isinstance(result_content, (dict, list)):
                        result_content = json.dumps(result_content, ensure_ascii=False)
                    else:
                        result_content = str(result_content)
                    
            except Exception as e:
                result_content = f"Error executing tool {tool_name}: {str(e)}"
        else:
            result_content = f"Error: Tool {tool_name} not found."
            
        tool_messages.append(ToolMessage(
            tool_call_id=call_id,
            content=result_content,
            name=tool_name
        ))
        
    return {"messages": tool_messages}
