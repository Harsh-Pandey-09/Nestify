from sqlalchemy.orm import Session

from app.models.chat import ChatMessage
from app.models.interest import Interest, InterestStatus


def get_interest_or_404(db: Session, interest_id: int) -> Interest:
    from fastapi import HTTPException, status

    interest = db.query(Interest).filter(Interest.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found")
    return interest


def assert_chat_allowed(interest: Interest):
    from fastapi import HTTPException, status

    if interest.status != InterestStatus.accepted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chat is only available once the owner has accepted this interest",
        )


def assert_user_in_conversation(interest: Interest, user_id: int, owner_id: int):
    from fastapi import HTTPException, status

    if user_id not in (interest.tenant_id, owner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this conversation")


def persist_message(db: Session, interest_id: int, sender_id: int, message: str) -> ChatMessage:
    msg = ChatMessage(interest_id=interest_id, sender_id=sender_id, message=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db: Session, interest_id: int) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.interest_id == interest_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
