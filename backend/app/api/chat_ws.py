from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.plugin_manager import plugin_manager
from app.core.config import settings
import logging
import json
import asyncio
from typing import Dict, Tuple, Optional
from app.agent.executor import run_agent_graph
from app.agent.stream import BroadcastStreamHandler

logger = logging.getLogger(__name__)
router = APIRouter()

# Global State for Background Tasks
# Key: conversation_id
# Value: (Task, StreamHandler)
active_executions: Dict[str, Tuple[asyncio.Task, BroadcastStreamHandler]] = {}

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
    
    # State for this connection
    current_queue: Optional[asyncio.Queue] = None
    current_handler: Optional[BroadcastStreamHandler] = None
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Resume / Initialize Session
            conversation = None
            requested_id = conversation_id
            
            if conversation_id:
                conversation = await ChatHistoryService.ensure_conversation(session, conversation_id)
                conversation_id = conversation.id
                logger.info(f"Session active (Resuming): {conversation_id}")
                
                # Check if there's a background task running for this conversation
                if conversation_id in active_executions:
                    logger.info(f"Joining background task for {conversation_id}")
                    task, handler = active_executions[conversation_id]
                    if not task.done():
                        current_handler = handler
                        current_queue = await handler.subscribe()
                    else:
                        # Task finished but not cleaned up? Clean up.
                        del active_executions[conversation_id]
                
                # Notify frontend of ID if changed
                if requested_id and requested_id != conversation_id:
                    await websocket.send_json({
                        "type": "init",
                        "conversation_id": conversation_id,
                        "title": conversation.title or "New Conversation"
                    })
            
            # 2. Main Loop (Multiplexing Input and Output)
            receive_task = asyncio.create_task(websocket.receive_text())
            queue_task = None
            
            while True:
                # Prepare waitables
                waitables = [receive_task]
                if current_queue and not queue_task:
                    queue_task = asyncio.create_task(current_queue.get())
                
                if queue_task:
                    waitables.append(queue_task)
                
                done, pending = await asyncio.wait(waitables, return_when=asyncio.FIRST_COMPLETED)
                
                # Case A: WebSocket Input (User Message / Stop)
                if receive_task in done:
                    try:
                        data = receive_task.result()
                        # Immediately schedule next receive to avoid gap
                        receive_task = asyncio.create_task(websocket.receive_text())
                        
                        request_payload = json.loads(data)
                        
                        # STOP COMMAND
                        if request_payload.get("type") == "stop":
                            logger.info(f"Stop requested for {conversation_id}")
                            if conversation_id in active_executions:
                                bg_task, _ = active_executions[conversation_id]
                                bg_task.cancel()
                            continue
                            
                        # USER MESSAGE
                        user_messages = request_payload.get("messages", [])
                        if not user_messages: continue
                        
                        # Lazy Creation if needed
                        if not conversation_id:
                            first_msg_content = user_messages[-1]["content"] if user_messages else "New Conversation"
                            title = first_msg_content[:50] + "..." if len(first_msg_content) > 50 else first_msg_content
                            conversation = await ChatHistoryService.create_conversation(session, title=title)
                            conversation_id = conversation.id
                            await websocket.send_json({"type": "init", "conversation_id": conversation_id, "title": title})

                        # Persist User Message
                        new_user_msg = user_messages[-1]
                        if new_user_msg["role"] == "user":
                            await ChatHistoryService.add_message(session, conversation_id, "user", new_user_msg["content"])
                        
                        # Prepare Background Execution
                        # 1. Cancel previous if running?
                        if conversation_id in active_executions:
                            old_task, old_handler = active_executions[conversation_id]
                            if not old_task.done():
                                old_task.cancel()
                        
                        # 2. Create New Handler & Task
                        new_handler = BroadcastStreamHandler()
                        current_handler = new_handler
                        current_queue = await new_handler.subscribe()
                        # If we had a queue task waiting on old queue, cancel it
                        if queue_task:
                            queue_task.cancel()
                            queue_task = None
                        
                        # Define the task wrapper to clean up self
                        async def background_wrapper(cid, h, msg):
                            try:
                                # Create a separate session for the background task since the WS session might close
                                async with AsyncSessionLocal() as bg_session:
                                    await run_agent_graph(h, cid, msg, session=bg_session)
                            except asyncio.CancelledError:
                                logger.info(f"Task {cid} cancelled")
                                # Error handling handled in run_agent_graph
                            except Exception as e:
                                logger.error(f"Task {cid} error: {e}")
                            finally:
                                if cid in active_executions:
                                    # Only delete if it's still us (not replaced)
                                    if active_executions.get(cid) == (asyncio.current_task(), h):
                                        del active_executions[cid]
                        
                        bg_task = asyncio.create_task(background_wrapper(conversation_id, new_handler, new_user_msg["content"]))
                        active_executions[conversation_id] = (bg_task, new_handler)
                        
                    except WebSocketDisconnect:
                        raise # Handle out of loop
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        logger.error(f"Input Error: {e}")
                        # Re-create receive task if it failed due to non-disconnect error
                        if receive_task.done():
                             receive_task = asyncio.create_task(websocket.receive_text())

                # Case B: Queue Output (Agent Stream)
                if queue_task in done:
                    try:
                        msg = queue_task.result()
                        queue_task = None # Ready for next
                        await websocket.send_json(msg)
                    except asyncio.CancelledError:
                        queue_task = None
                    except Exception as e:
                        logger.error(f"Queue Error: {e}")
                        queue_task = None
                
                # NOTE: We DO NOT cancel pending tasks here.
                # receive_task stays pending if queue triggered.
                # queue_task stays pending if input triggered.

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            # NOTE: We DO NOT cancel the background task here! It continues running.
            if conversation_id:
                manager.disconnect(websocket, conversation_id)
            # Unsubscribe from handler
            if current_handler and current_queue:
                current_handler.unsubscribe(current_queue)
                
        except Exception as e:
            logger.exception(f"WebSocket Error: {e}")
            try: await websocket.send_json({"type": "error", "content": str(e)})
            except: pass
