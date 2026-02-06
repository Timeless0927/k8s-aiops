from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.plugin_manager import plugin_manager
from app.core.config import settings
import logging
import json
from app.agent.executor import run_agent_graph

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/chat/ws")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str | None = None):
    await websocket.accept()
    logger.info(f"WebSocket connected. Request Conversation ID: {conversation_id}")
    
    # Register connection for global broadcasting (e.g. Alerts)
    from app.services.connection_manager import manager
    if conversation_id:
        await manager.connect(websocket, conversation_id)
    
    # DB Session per connection
    from app.db.session import AsyncSessionLocal
    from app.services.chat_history import ChatHistoryService
    
    async with AsyncSessionLocal() as session:
        try:
            # Resume existing or Lazy Create
            # If conversation_id is None, we DO NOT create it yet.
            # We wait for the first message to create it.
            conversation = None
            requested_id = conversation_id
            
            if conversation_id:
                conversation = await ChatHistoryService.ensure_conversation(session, conversation_id)
                conversation_id = conversation.id
                logger.info(f"Session active (Resuming): {conversation_id}")
                
                # If requested ID was invalid (and we got a new one), notify frontend
                if requested_id and requested_id != conversation_id:
                    logger.warning(f"Requested ID {requested_id} not found. Created new: {conversation_id}")
                    await websocket.send_json({
                        "type": "init",
                        "conversation_id": conversation_id,
                        "title": conversation.title or "New Conversation"
                    })
            else:
                logger.info("Session active (New/Lazy): Waiting for first message...")
            
            while True:
                # 1. Receive User Message
                data = await websocket.receive_text()
                try:
                    request_payload = json.loads(data)
                    user_messages = request_payload.get("messages", [])
                    # model param ignored, we use setting in executor
                    
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "content": "Invalid JSON format"})
                    continue

                if not user_messages:
                    continue
                
                # Lazy Creation Check
                if not conversation_id:
                    # Auto-Title: Use first message content (truncated)
                    first_msg_content = user_messages[-1]["content"] if user_messages else "New Conversation"
                    title = first_msg_content[:50] + "..." if len(first_msg_content) > 50 else first_msg_content
                    
                    conversation = await ChatHistoryService.create_conversation(session, title=title)
                    conversation_id = conversation.id
                    logger.info(f"Session initialized (First Message): {conversation_id} - Title: {title}")
                    
                    # Notify Frontend of the new Conversation ID
                    await websocket.send_json({
                        "type": "init",
                        "conversation_id": conversation_id,
                        "title": title
                    })

                # 1.1 Persist User Messages (Only the new ones)
                # Frontend sends FULL history usually. We should identify specific new message.
                # Simplification: Assume the LAST message in user_messages is the new one.
                new_user_msg = user_messages[-1]
                if new_user_msg["role"] == "user":
                    await ChatHistoryService.add_message(
                        session, conversation_id, "user", new_user_msg["content"]
                    )
                
                # 2. Execute Agent Logic via LangGraph
                await run_agent_graph(websocket, conversation_id, new_user_msg["content"], session=session)
                    
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            if conversation_id:
                manager.disconnect(websocket, conversation_id)
        except Exception as e:
            logger.exception(f"WebSocket Error: {e}")
            try:
                await websocket.send_json({"type": "error", "content": str(e)})
            except:
                pass
