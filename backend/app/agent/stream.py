import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class StreamHandler(ABC):
    """
    Abstract base class for handling agent stream output.
    Decouples the agent from the specific output mechanism (WebSocket, CLI, etc.)
    """
    @abstractmethod
    async def send(self, data: Dict[str, Any]):
        pass

class BroadcastStreamHandler(StreamHandler):
    """
    Broadcasts events to multiple listeners (WebSockets).
    Supports late-joining listeners by buffering recent critical events (optional, for now just realtime).
    """
    def __init__(self):
        self.listeners: List[asyncio.Queue] = []
        self._buffer: List[Dict[str, Any]] = [] # Optional: Keep last N events?
    
    async def subscribe(self) -> asyncio.Queue:
        """
        Creates a new queue for a listener and registers it.
        """
        queue = asyncio.Queue()
        self.listeners.append(queue)
        
        # Optional: Replay history if needed?
        # For now, we rely on DB history fetch for past events.
        # This handler is strictly for REAL-TIME events.
        return queue
    
    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.listeners:
            self.listeners.remove(queue)
    
    async def send(self, data: Dict[str, Any]):
        """
        Broadcast data to all active listeners.
        """
        # Prune closed listeners (if any)
        # Actually unsubscribe should handle it.
        
        msg = json.dumps(data) if not isinstance(data, str) else data
        
        # Buffer (limit 50?)
        # self._buffer.append(data)
        # if len(self._buffer) > 50: self._buffer.pop(0)
        
        for queue in self.listeners:
            try:
                # Non-blocking put
                queue.put_nowait(data)
            except asyncio.QueueFull:
                logger.warning("Listener queue full, dropping message")
                pass
