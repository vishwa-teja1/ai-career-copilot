"""
Minimal email sender. Falls back to logging the OTP to console when SMTP
isn't configured, so local dev works with zero setup - swap in
SES/SendGrid/Postmark here for production without touching callers.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_otp_email(to_email: str, otp_code: str) -> None:
    subject = "Your AI Career Copilot verification code"
    body = (
        f"Your verification code is: {otp_code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
        f"If you didn't request this, you can safely ignore this email."
    )

    if not settings.SMTP_HOST:
        # Dev fallback - makes the OTP flow testable without a mail server.
        logger.info("[DEV EMAIL] To: %s | Subject: %s | Code: %s", to_email, subject, otp_code)
        return

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
