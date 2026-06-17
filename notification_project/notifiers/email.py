"""
notifiers/email.py — SMTP email notifier.
"""

import smtplib
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import Config
from models import NotificationRecord


def _build_message(record: NotificationRecord) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "\u26a0\ufe0f Warning: {}".format(record.name)
    msg["From"] = Config.EMAIL_FROM
    msg["To"] = Config.EMAIL_TO

    meta_plain = "\n".join("  {}: {}".format(k, v) for k, v in record.metadata.items())
    plain = "WARNING: {name}\n\n{description}\n\nID: {id}\nReceived: {received}\n{meta}".format(
        name=record.name, description=record.description,
        id=record.id, received=record.received_at.isoformat(), meta=meta_plain)

    meta_html = "".join(
        "<tr><td><b>{}</b></td><td>{}</td></tr>".format(k, v)
        for k, v in record.metadata.items())
    html = """<html><body>
      <h2 style="color:#e67e22;">\u26a0\ufe0f Warning: {name}</h2>
      <p>{description}</p>
      <table border="1" cellpadding="4" cellspacing="0">
        <tr><td><b>ID</b></td><td>{id}</td></tr>
        <tr><td><b>Received</b></td><td>{received}</td></tr>
        {meta}
      </table></body></html>""".format(
        name=record.name, description=record.description,
        id=record.id, received=record.received_at.isoformat(), meta=meta_html)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def send(record: NotificationRecord) -> None:
    msg = _build_message(record)
    if Config.SIMULATION_MODE:
        print("\n[Email SIMULATION] Would send:")
        print("  From: {}  To: {}  Subject: {}".format(msg["From"], msg["To"], msg["Subject"]))
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print("\n--- body ---\n{}".format(part.get_payload()))
        print("[Email SIMULATION] End\n")
        return
    # --- Real send -----------------------------------------------------------
    with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
        server.ehlo()
        server.starttls()
        if Config.SMTP_USER:
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        server.sendmail(Config.EMAIL_FROM, Config.EMAIL_TO, msg.as_string())
