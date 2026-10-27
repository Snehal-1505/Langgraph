import asyncio
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class EventBroadcaster:
    """Manages active Server-Sent Events (SSE) queues for research sessions."""

    def __init__(self):
        # Maps session_id -> list of asyncio.Queue
        self._listeners: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """Register a new SSE client queue for a specific research session."""
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            if session_id not in self._listeners:
                self._listeners[session_id] = []
            self._listeners[session_id].append(queue)
        logger.debug(f"Client subscribed to session {session_id}. Total listeners: {len(self._listeners[session_id])}")
        return queue

    async def unsubscribe(self, session_id: str, queue: asyncio.Queue):
        """Remove a disconnected SSE client queue."""
        async with self._lock:
            if session_id in self._listeners:
                if queue in self._listeners[session_id]:
                    self._listeners[session_id].remove(queue)
                if not self._listeners[session_id]:
                    del self._listeners[session_id]
        logger.debug(f"Client unsubscribed from session {session_id}.")

    async def broadcast(self, session_id: str, event_data: Dict[str, Any]):
        """Publish a real workflow event to all connected SSE clients for the session."""
        async with self._lock:
            queues = list(self._listeners.get(session_id, []))

        if not queues:
            return

        payload = json.dumps(event_data)
        for q in queues:
            try:
                await q.put(payload)
            except Exception as e:
                logger.warning(f"Failed to push SSE event to queue: {e}")


# Global singleton instance
event_broadcaster = EventBroadcaster()
