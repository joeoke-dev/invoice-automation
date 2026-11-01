"""Send a receipt PDF by email through Gmail's SMTP server."""

import os
import re
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def valid_email(address):
    return isinstance(address, str) and bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", address))


def get_credentials():
    """Read credentials from environment variables (never hardcode them)."""
    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender or not password:
        raise RuntimeError(
            "Set the GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables "
            "before using --send."
        )
    return sender, password


def send_receipt(receipt, pdf_path, to_address, sender, password):
    msg = EmailMessage()
    msg["Subject"] = f"Your receipt {receipt.invoice_no}"
    msg["From"] = sender
    msg["To"] = to_address
    msg.set_content(
        "Hello,\n\n"
        f"Thank you for shopping at {receipt.mall}.\n"
        f"Your receipt {receipt.invoice_no} is attached.\n"
        f"Total: {receipt.total():,.2f}\n"
    )

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=f"receipt_{receipt.invoice_no}.pdf",
        )

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender, password)
        server.send_message(msg)
