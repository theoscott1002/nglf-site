import base64
import os
from email.message import EmailMessage

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_admin_notification(subject: str, body: str) -> None:
    admin_to = os.getenv("ADMIN_NOTIFY_EMAIL")
    from_email = os.getenv("FROM_EMAIL")  # should be same as the authorized Gmail account

    # If not configured, do nothing (dev-friendly)
    if not admin_to or not from_email:
        return

    # Load credentials from token.json and refresh if needed
    if not os.path.exists("token.json"):
        raise RuntimeError("token.json not found. Run oauth_bootstrap.py first.")

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    msg = EmailMessage()
    msg["To"] = admin_to
    msg["From"] = from_email
    msg["Subject"] = subject
    msg.set_content(body)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
