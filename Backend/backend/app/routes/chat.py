import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.core.security import decode_access_token
from app.dependencies import get_current_user
from app.models.user import User
from app.models.listing import Listing
from app.models.notification import NotificationType
from app.schemas.chat import ChatHistoryResponse, ChatMessageResponse
from app.services import chat_service, notification_service
from app.websocket.manager import manager

router = APIRouter(tags=["Chat"])


@router.get("/api/chat/{interest_id}/messages", response_model=ChatHistoryResponse)
def get_chat_messages(interest_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    interest = chat_service.get_interest_or_404(db, interest_id)
    listing = db.query(Listing).filter(Listing.id == interest.listing_id).first()
    chat_service.assert_user_in_conversation(interest, current_user.id, listing.owner_id)
    chat_service.assert_chat_allowed(interest)

    messages = chat_service.get_chat_history(db, interest_id)
    return ChatHistoryResponse(
        interest_id=interest_id, messages=[ChatMessageResponse.model_validate(m) for m in messages]
    )


def _authenticate_ws_user(token: str, db: Session) -> User | None:
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()


@router.websocket("/ws/chat/{interest_id}")
async def chat_websocket(websocket: WebSocket, interest_id: int, token: str = Query(...)):
    """
    Connect with: ws://<host>/ws/chat/{interest_id}?token=<JWT access token>
    Client sends: {"message": "hello"}
    Server broadcasts: {"type": "message", "data": {...ChatMessageResponse}}
    """
    db = SessionLocal()
    try:
        user = _authenticate_ws_user(token, db)
        if not user:
            await websocket.close(code=4001)
            return

        interest = chat_service.get_interest_or_404(db, interest_id)
        listing = db.query(Listing).filter(Listing.id == interest.listing_id).first()

        try:
            chat_service.assert_user_in_conversation(interest, user.id, listing.owner_id)
            chat_service.assert_chat_allowed(interest)
        except Exception:
            await websocket.close(code=4003)
            return

        await manager.connect(interest_id, user.id, websocket)
        await websocket.send_json({"type": "connected", "data": {"interest_id": interest_id, "user_id": user.id}})

        try:
            while True:
                raw = await websocket.receive_text()
                payload = json.loads(raw)
                msg_type = payload.get("type", "message")

                if msg_type == "message":
                    text = (payload.get("message") or "").strip()
                    if not text:
                        continue
                    saved = chat_service.persist_message(db, interest_id, user.id, text)

                    out = {
                        "type": "message",
                        "data": ChatMessageResponse.model_validate(saved).model_dump(mode="json"),
                    }
                    await manager.send_to_all(interest_id, out)

                    # Notify the other participant (in-app notification; email optional/omitted for chat spam control)
                    other_user_id = listing.owner_id if user.id == interest.tenant_id else interest.tenant_id
                    other_user = db.query(User).filter(User.id == other_user_id).first()
                    if other_user:
                        await notification_service.create_notification(
                            db,
                            other_user,
                            notif_type=NotificationType.new_message,
                            message=f"New message from {user.name}",
                            send_email=False,
                        )

                elif msg_type == "typing":
                    await manager.broadcast(
                        interest_id, {"type": "typing", "data": {"user_id": user.id}}, exclude=websocket
                    )

        except WebSocketDisconnect:
            manager.disconnect(interest_id, websocket)
    finally:
        db.close()
