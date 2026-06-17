"""
notifiers/slack.py — Slack Incoming Webhook notifier.

Setup (one-time):
  1. https://api.slack.com/apps -> Create New App -> From scratch
  2. Pick your "notifications" workspace
  3. Left sidebar -> Incoming Webhooks -> turn On
  4. "Add New Webhook to Workspace" -> select #all-notifications -> Allow
  5. Copy the URL it gives you (https://hooks.slack.com/services/T.../B.../XXXX)

To send for real:
  1. Set SIMULATION_MODE=false
  2. Set SLACK_WEBHOOK_URL to the URL from step 5 above
"""

import json
import urllib.request
from typing import Any, Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config
from models import NotificationRecord


def _build_payload(record: NotificationRecord) -> Dict[str, Any]:
    """
    Build a Slack message payload using Block Kit.
    See: https://api.slack.com/block-kit
    """
    fields = [
        {"type": "mrkdwn", "text": "*ID:*\n{}".format(record.id)},
        {"type": "mrkdwn", "text": "*Received:*\n{}".format(record.received_at.isoformat())},
    ]
    for k, v in record.metadata.items():
        fields.append({"type": "mrkdwn", "text": "*{}:*\n{}".format(k, v)})

    return {
        "text": "\u26a0\ufe0f Warning: {}".format(record.name),  # fallback for notifications/search
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "\u26a0\ufe0f {}".format(record.name)},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": record.description},
            },
            {
                "type": "section",
                "fields": fields,
            },
        ],
    }


def send(record: NotificationRecord) -> None:
    """Forward notification to Slack (or simulate)."""
    payload = _build_payload(record)

    if Config.SIMULATION_MODE:
        print("\n[Slack SIMULATION] Would POST to: {}".format(
            Config.SLACK_WEBHOOK_URL or "<SLACK_WEBHOOK_URL not set>"
        ))
        print(json.dumps(payload, indent=2, default=str))
        print("[Slack SIMULATION] End\n")
        return

    # --- Real send -----------------------------------------------------------
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        Config.SLACK_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8")
        if resp.status != 200 or body != "ok":
            raise RuntimeError("Slack webhook returned HTTP {}: {}".format(resp.status, body))
    # -------------------------------------------------------------------------
