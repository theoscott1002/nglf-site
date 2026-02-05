import os
import smtplib
from email.message import EmailMessage

def send_admin_notification(subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    to_email = os.getenv("ADMIN_NOTIFY_EMAIL")
    from_email = os.getenv("FROM_EMAIL", user)

    # If not configured, silently do nothing (useful during dev)
    if not all([host, port, user, password, to_email, from_email]):
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
