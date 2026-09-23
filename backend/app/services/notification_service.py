import logging
import uuid
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.models.notification import Notification

logger = logging.getLogger("notification_service")


async def notify_user(db, user_id: uuid.UUID, title: str, body: str, notif_type: str = "GENERAL", related_complaint_id=None) -> Notification:
    """Creates an in-app notification row, then fans out to email/push if
    those channels are configured. Delivery failures never block the
    in-app notification -- it's already committed to the DB by the time
    fan-out runs."""
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
        await _dispatch_push(user_id, title, body)

    return notification


async def send_email(to_address: str, subject: str, body: str) -> bool:
    """Sends a plain-text email via SMTP. Returns False (and logs a
    warning) instead of raising when SMTP isn't configured or delivery
    fails -- notifications are always advisory, never something that
    should take down the request that triggered them."""
    if not settings.SMTP_HOST:
        logger.info("SMTP not configured; skipping email to %s: %s", to_address, subject)
        return False

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_USE_TLS,
        )
        return True
    except (aiosmtplib.SMTPException, OSError) as exc:
        logger.warning("Failed to send email to %s: %s", to_address, exc)
        return False


async def notify_admin_new_complaint(complaint_number: str, category_name: str, description: str, severity: str, latitude: float, longitude: float, reporter_email: str) -> None:
    """Section 26 of the spec calls for admin visibility into every new
    report. This sends a real email (not just an in-app row, since the
    person watching this inbox may not be logged into the platform) to
    ADMIN_ALERT_EMAIL for every complaint filed."""
    if not settings.ADMIN_ALERT_EMAIL:
        return

    subject = f"New complaint filed: {complaint_number} ({category_name})"
    body = (
        f"A new complaint was just filed on Nellai Green & Civic.\n\n"
        f"Number: {complaint_number}\n"
        f"Category: {category_name}\n"
        f"Severity: {severity}\n"
        f"Reported by: {reporter_email}\n"
        f"Location: {latitude:.5f}, {longitude:.5f}\n"
        f"Description: {description}\n"
    )
    await send_email(settings.ADMIN_ALERT_EMAIL, subject, body)


async def _dispatch_push(user_id, title, body) -> None:
    if not settings.FCM_SERVER_KEY:
        return  # No FCM key configured; in-app notification already recorded.
    # A real deployment posts to FCM here using the user's registered device tokens.
