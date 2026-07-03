import logging

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.core.config import settings

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an email; returns True/False instead of raising, so a failed
    email never breaks the core request flow (interest/accept/decline etc).
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body_html,
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


def high_match_interest_email(owner_name: str, tenant_name: str, listing_title: str, score: float) -> tuple[str, str]:
    subject = f"High compatibility match ({score:.0f}%) on your listing '{listing_title}'"
    body = f"""
    <p>Hi {owner_name},</p>
    <p><strong>{tenant_name}</strong> has expressed interest in your listing
    <strong>{listing_title}</strong> with an AI compatibility score of
    <strong>{score:.0f}/100</strong>.</p>
    <p>Log in to review their profile and respond.</p>
    """
    return subject, body


def interest_received_email(owner_name: str, tenant_name: str, listing_title: str) -> tuple[str, str]:
    subject = f"New interest in your listing '{listing_title}'"
    body = f"""
    <p>Hi {owner_name},</p>
    <p><strong>{tenant_name}</strong> has expressed interest in your listing
    <strong>{listing_title}</strong>.</p>
    <p>Log in to review and respond.</p>
    """
    return subject, body


def interest_decision_email(tenant_name: str, listing_title: str, accepted: bool) -> tuple[str, str]:
    status_text = "accepted" if accepted else "declined"
    subject = f"Your interest in '{listing_title}' was {status_text}"
    body = f"""
    <p>Hi {tenant_name},</p>
    <p>The owner has <strong>{status_text}</strong> your interest in
    <strong>{listing_title}</strong>.</p>
    {"<p>You can now chat with the owner in real time on the platform.</p>" if accepted else ""}
    """
    return subject, body
