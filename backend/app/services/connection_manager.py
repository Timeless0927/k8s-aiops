
import asyncio
from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat.
    Allows broadcasting from background tasks (alerts) to connected frontend clients.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            # Map conversation_id -> List[WebSocket]
            cls._instance.active_connections: Dict[str, List[WebSocket]] = {}
        return cls._instance

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Register a connection."""
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
        logger.info(f"Client connected to stream: {conversation_id} (Total: {len(self.active_connections[conversation_id])})")

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Remove a connection."""
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
        logger.info(f"Client disconnected from stream: {conversation_id}")

    async def broadcast_json(self, conversation_id: str, data: dict):
        """
        Send JSON data to all clients listening to this conversation data.
        Currently used by AlertQueue to stream Agent progress to the UI.
        """
        if conversation_id in self.active_connections:
            # Clone list to avoid modification during iteration
            for connection in self.active_connections[conversation_id][:]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    # Likely disconnected, cleanup?
                    # disconnect() is usually called by the endpoint handling the socket.
                    pass

manager = ConnectionManager()
