import smtplib
from email.mime.text import MIMEText
from ..core.settings import settings
from ..core.logger import logger


def send_email(to_email: str, subject: str, html: str):
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
    logger.info({"event": "email_sent", "to": to_email, "subject": subject})
