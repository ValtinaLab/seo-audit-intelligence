from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

import requests


def send_alerts(alerts: list[str]) -> bool:
    if not alerts:
        return False
    sent = False
    if os.getenv("SLACK_WEBHOOK_URL"):
        sent = _send_slack(alerts) or sent
    if os.getenv("SMTP_HOST") and os.getenv("ALERT_EMAIL_TO"):
        sent = _send_email(alerts) or sent
    return sent


def _send_slack(alerts: list[str]) -> bool:
    try:
        response = requests.post(
            os.environ["SLACK_WEBHOOK_URL"],
            json={"text": "*Alertas SEO criticas*\n" + "\n".join(f"- {alert}" for alert in alerts)},
            timeout=10,
        )
        return response.status_code < 400
    except requests.RequestException:
        return False


def _send_email(alerts: list[str]) -> bool:
    message = EmailMessage()
    message["Subject"] = "Alertas SEO criticas"
    message["From"] = os.getenv("ALERT_EMAIL_FROM", os.getenv("SMTP_USER", "seo-audit@example.com"))
    message["To"] = os.environ["ALERT_EMAIL_TO"]
    message.set_content("\n".join(f"- {alert}" for alert in alerts))

    try:
        with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587"))) as smtp:
            smtp.starttls()
            if os.getenv("SMTP_USER"):
                smtp.login(os.environ["SMTP_USER"], os.getenv("SMTP_PASSWORD", ""))
            smtp.send_message(message)
        return True
    except OSError:
        return False
