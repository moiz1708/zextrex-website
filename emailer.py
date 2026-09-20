"""
Sends the website's contact-form messages to Zextrex support, using
Gmail's SMTP server.

SETUP (Gmail requires an "App Password", not your normal login password):
    1. Turn on 2-Step Verification on the Gmail account you want to send
       FROM (this can be zextrextechnology@gmail.com itself, or any Gmail
       account you control — it does not have to be the address that
       receives the messages).
    2. Go to https://myaccount.google.com/apppasswords and create an
       app password for "Mail".
    3. Put that account and the 16-character app password in your .env
       file:
           SMTP_EMAIL=your-sending-address@gmail.com
           SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx
    4. CONTACT_TO_EMAIL in .env controls who receives these messages —
       it already defaults to zextrexsupport@gmail.com below.

Until SMTP_EMAIL / SMTP_APP_PASSWORD are set, send_contact_email() raises
a clear error, which the /api/contact route in app.py turns into a
message shown in the contact form itself.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "").strip()
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").strip()
CONTACT_TO_EMAIL = os.getenv("CONTACT_TO_EMAIL", "zextrexsupport@gmail.com").strip()


def send_contact_email(sender_email: str, message: str) -> None:
    """Send one contact-form message. Raises RuntimeError/OSError on failure."""
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "Email sending isn't configured yet — add SMTP_EMAIL and "
            "SMTP_APP_PASSWORD to your .env file (see emailer.py for "
            "step-by-step setup)."
        )

    body = (
        "New message from the Zextrex Technology website contact form.\n\n"
        f"From: {sender_email}\n\n"
        f"Message:\n{message}\n"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "New message from the Zextrex Technology website"
    msg["From"] = formataddr(("Zextrex Website", SMTP_EMAIL))
    msg["To"] = CONTACT_TO_EMAIL
    msg["Reply-To"] = sender_email  # replying goes straight to the visitor

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [CONTACT_TO_EMAIL], msg.as_string())
