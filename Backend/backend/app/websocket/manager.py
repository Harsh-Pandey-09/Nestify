from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """
    Tracks active WebSocket connections per chat room (interest_id).
    Each 'room' represents the tenant<->owner conversation for one
    accepted interest.
    """

    def __init__(self):
        self.rooms: Dict[int, Set[WebSocket]] = defaultdict(set)
        # maps websocket -> user_id, useful for broadcasting sender info
        self.socket_users: Dict[WebSocket, int] = {}

    async def connect(self, interest_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms[interest_id].add(websocket)
        self.socket_users[websocket] = user_id

    def disconnect(self, interest_id: int, websocket: WebSocket):
        self.rooms[interest_id].discard(websocket)
        self.socket_users.pop(websocket, None)
        if not self.rooms[interest_id]:
            del self.rooms[interest_id]

    async def broadcast(self, interest_id: int, payload: dict, exclude: WebSocket = None):
        dead_sockets = []
        for ws in self.rooms.get(interest_id, set()):
            if ws is exclude:
                continue
            try:
                await ws.send_json(payload)
            except Exception:  # noqa: BLE001
                dead_sockets.append(ws)
        for ws in dead_sockets:
            self.disconnect(interest_id, ws)

    async def send_to_all(self, interest_id: int, payload: dict):
        await self.broadcast(interest_id, payload, exclude=None)


manager = ConnectionManager()
