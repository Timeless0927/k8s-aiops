from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, Message
from typing import List
import httpx
from app.core.config import settings
from pydantic import BaseModel
import logging
from app.services.plugin_manager import plugin_manager
# from app.agent.tools import TOOLS_SCHEMA, AVAILABLE_TOOLS # Deprecated static import

import json

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Conversation Management Models ---
class ConversationItem(BaseModel):
    id: str
    title: str
    created_at: str # ISO format

class MessageItem(BaseModel):
    role: str
    content: str | None
    created_at: str

# --- Endpoints ---

@router.get("/conversations", response_model=List[ConversationItem])
async def list_conversations():
    """List recent conversations."""
    from app.db.session import AsyncSessionLocal
    from app.db.models.chat import Conversation
    from sqlalchemy import select, desc
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.type == "chat")
            .order_by(desc(Conversation.created_at))
            .limit(50)
        )
        conversations = result.scalars().all()
        return [
            ConversationItem(
                id=c.id, 
                title=c.title or "Untitled", 
                created_at=c.created_at.isoformat()
            ) for c in conversations
        ]

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageItem])
async def get_conversation_messages(conversation_id: str):
    """Get messages for a specific conversation."""
    from app.db.session import AsyncSessionLocal
    from app.services.chat_history import ChatHistoryService
    
    async with AsyncSessionLocal() as session:
        # Check if conversation exists
        conv = await ChatHistoryService.get_conversation(session, conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = await ChatHistoryService.get_recent_messages(session, conversation_id, limit=100)
        return [
            MessageItem(
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat()
            ) for m in messages
        ]

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    from app.db.session import AsyncSessionLocal
    from app.services.chat_history import ChatHistoryService
    
    async with AsyncSessionLocal() as session:
        success = await ChatHistoryService.delete_conversation(session, conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "deleted", "id": conversation_id}


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Agentic Chat Endpoint with Tool Calling (ReAct Loop)
    """
    try:
        # Get latest tools from PluginManager dynamically
        current_tools_schema = plugin_manager.get_all_tools_schema()
        current_tools_registry = plugin_manager.tools_registry
        
        # History prep
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        url = f"{settings.OPENAI_BASE_URL}/chat/completions"
        
        async with httpx.AsyncClient() as client:
            # System Prompt for Anti-Hallucination & Tool Use
            system_prompt = {
                "role": "system",
                "content": """
You are a Kubernetes AIOps Agent specialized in troubleshooting.
CRITICAL RULES:
1. FACTUALITY: Do NOT invent, guess, or hallucinate labels, pod names, or error messages.
2. EVIDENCE: You must run `run_kubectl` to verify facts. If you don't see a label in the output, it DOES NOT EXIST.
3. ADMIT DEFEAT: If you cannot find the info, say "I cannot find X in the cluster". Do not make it up.
4. SYNTAX: When running kubectl, use correct JSON/YAML flags if parsing is needed, but plain text is fine for summary.
5. DIAGNOSTICS: If the user asks to "scan", "diagnose", or "check health", use `run_k8sgpt`. It returns raw JSON findings. You must ANALYZE this JSON and explain the issues to the user in simple terms. Do not just dump the JSON.
6. VERIFICATION: After taking ANY action (delete pod, restart deployment, etc.), you MUST run `run_kubectl` again to check the new status. Do NOT assume it worked. Do NOT invent a new pod name. Fetch it.
"""
            }
            
            # Prepend System Prompt
            if messages[0]["role"] != "system":
                messages.insert(0, system_prompt)

            # --- Agentic ReAct Loop ---
            MAX_ITERATIONS = 10
            iteration = 0
            
            while iteration < MAX_ITERATIONS:
                iteration += 1
                logger.info(f"--- Iteration {iteration} of {MAX_ITERATIONS} ---")

                payload = {
                    "model": request.model or settings.MODEL_NAME,
                    "messages": messages,
                    "temperature": 0.1, 
                    "tools": current_tools_schema,
                    "tool_choice": "auto"
                }
                
                resp = await client.post(url, json=payload, headers=headers, timeout=60.0)
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail=resp.text)
                    
                resp_data = resp.json()
                choice = resp_data["choices"][0]
                
                # Robust parsing
                if isinstance(choice, str):
                     msg = {"content": choice, "role": "assistant"}
                elif isinstance(choice, dict):
                     msg = choice.get("message", {})
                     if isinstance(msg, str): msg = {"content": msg, "role": "assistant"}
                else:
                     msg = {"content": str(choice), "role": "assistant"}
                
                # Append Assistant Message to History
                messages.append(msg)
                
                # Check for Tool Calls
                tool_calls = msg.get("tool_calls")
                
                if not tool_calls:
                    # No tools called -> Final Answer
                    logger.info("Agent decided to stop (no tool calls).")
                    content = msg.get("content")
                    if not content: content = "Empty response."
                    return ChatResponse(response=content)
                
                # Execute Tools and Keep Looping
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    raw_args = tool_call["function"]["arguments"]
                    call_id = tool_call["id"]
                    
                    logger.info(f"Agent executing tool: {func_name}({raw_args})")
                    
                    if func_name in current_tools_registry:
                        try:
                            # Handle potential JSON parsing errors in arguments
                            args = json.loads(raw_args)
                            result_str = current_tools_registry[func_name](**args)
                        except json.JSONDecodeError:
                             result_str = f"Error: Invalid JSON arguments: {raw_args}"
                        except Exception as e:
                            logger.exception(f"Tool execution failed: {e}")
                            result_str = f"Error executing {func_name}: {str(e)}"
                    else:
                        result_str = f"Error: Tool {func_name} not found."

                    # Append Result
                    # Truncate if huge (e.g. k8sgpt full json might be big)
                    # We'll allow it for now, assuming local model context is sufficient
                    
                    messages.append({
                        "role": "tool",
                        "content": result_str,
                        "tool_call_id": call_id
                    })
                
                # Loop continues... sends (User + Assistant + ToolResults) back to LLM

            # If loop limits reached
            logger.warning(f"Max iterations {MAX_ITERATIONS} reached.")
            return ChatResponse(response="I'm sorry, I reached my maximum thinking steps before finding a final answer.")

    except Exception as e:
        logger.exception(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
