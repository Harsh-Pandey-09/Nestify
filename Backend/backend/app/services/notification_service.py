from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services import email_service


async def create_notification(
    db: Session, user: User, notif_type: NotificationType, message: str, send_email: bool = True
) -> Notification:
    notification = Notification(user_id=user.id, type=notif_type, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)

    if send_email and user.email:
        subject, body = _build_email_content(notif_type, message)
        sent = await email_service.send_email(user.email, subject, body)
        notification.email_sent = sent
        db.commit()
        db.refresh(notification)

    return notification


def _build_email_content(notif_type: NotificationType, message: str) -> tuple[str, str]:
    subject_map = {
        NotificationType.high_match_interest: "High compatibility match on your listing",
        NotificationType.interest_received: "New interest in your listing",
        NotificationType.interest_accepted: "Your interest was accepted",
        NotificationType.interest_declined: "Your interest was declined",
        NotificationType.new_message: "New chat message",
        NotificationType.listing_filled: "Listing marked as filled",
    }
    subject = subject_map.get(notif_type, "Nestify notification")
    body = f"<p>{message}</p>"
    return subject, body


async def notify_owner_of_interest(db: Session, owner: User, tenant_name: str, listing_title: str, score: float):
    high_match = score >= settings.HIGH_MATCH_THRESHOLD
    notif_type = NotificationType.high_match_interest if high_match else NotificationType.interest_received
    message = (
        f"{tenant_name} expressed interest in '{listing_title}' "
        f"(compatibility score: {score:.0f}/100)."
    )
    await create_notification(db, owner, notif_type, message, send_email=True)


async def notify_tenant_of_decision(db: Session, tenant: User, listing_title: str, accepted: bool):
    notif_type = NotificationType.interest_accepted if accepted else NotificationType.interest_declined
    status_text = "accepted" if accepted else "declined"
    message = f"Your interest in '{listing_title}' was {status_text} by the owner."
    await create_notification(db, tenant, notif_type, message, send_email=True)


async def notify_listing_filled(db: Session, owner: User, listing_title: str):
    message = f"Your listing '{listing_title}' has been marked as filled and is now hidden from search results."
    await create_notification(db, owner, NotificationType.listing_filled, message, send_email=False)
