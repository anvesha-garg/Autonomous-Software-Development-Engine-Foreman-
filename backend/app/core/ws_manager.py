import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("ws_manager")

class ConnectionManager:
    """Manages active WebSocket connections per project for streaming updates."""
    def __init__(self):
        # Maps project_id -> list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket client connected to project {project_id}")

    def disconnect(self, project_id: str, websocket: WebSocket) -> None:
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket client disconnected from project {project_id}")

    async def broadcast(self, project_id: str, message: dict) -> None:
        """Sends JSON payload to all clients connected to a specific project_id."""
        if project_id not in self.active_connections:
            return

        dead_sockets: List[WebSocket] = []
        payload = json.dumps(message)
        
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error broadcasting to socket: {e}")
                dead_sockets.append(connection)

        for dead in dead_sockets:
            self.disconnect(project_id, dead)

ws_manager = ConnectionManager()