import uuid

from app.core.config import settings
from app.models.notification import Notification


async def notify_user(db, user_id: uuid.UUID, title: str, body: str, notif_type: str = "GENERAL", related_complaint_id=None) -> Notification:
    """Creates an in-app notification row. Email/push delivery are pluggable
    fan-outs from here (kept as no-op stubs when SMTP/FCM aren't configured
    so the demo works without external credentials)."""
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        type=notif_type,
        related_complaint_id=related_complaint_id,
    )
    db.add(notification)
    await db.flush()

    if settings.NOTIFICATIONS_ENABLED:
        await _dispatch_email(user_id, title, body)
        await _dispatch_push(user_id, title, body)

    return notification


async def _dispatch_email(user_id, title, body) -> None:
    if not settings.SMTP_HOST:
        return  # No SMTP configured; in-app notification already recorded.
    # A real deployment plugs an SMTP/SES/SendGrid client in here.


async def _dispatch_push(user_id, title, body) -> None:
    if not settings.FCM_SERVER_KEY:
        return  # No FCM key configured; in-app notification already recorded.
    # A real deployment posts to FCM here using the user's registered device tokens.
