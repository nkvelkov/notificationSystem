"""
notifiers/teams.py — Microsoft Teams Incoming Webhook notifier.

To send for real:
  1. Set SIMULATION_MODE=false
  2. Set TEAMS_WEBHOOK_URL to your Teams Incoming Webhook URL
"""

import json
import urllib.request
from typing import Any, Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config
from models import NotificationRecord


def _build_payload(record: NotificationRecord) -> Dict[str, Any]:
    facts = [
        {"title": "ID",       "value": str(record.id)},
        {"title": "Received", "value": record.received_at.isoformat()},
    ]
    facts += [{"title": k, "value": str(v)} for k, v in record.metadata.items()]
    return {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "text": "\u26a0\ufe0f  {}".format(record.name),
                     "weight": "Bolder", "size": "Medium", "color": "Warning"},
                    {"type": "TextBlock", "text": record.description, "wrap": True},
                    {"type": "FactSet", "facts": facts},
                ],
            },
        }],
    }


def send(record: NotificationRecord) -> None:
    payload = _build_payload(record)
    if Config.SIMULATION_MODE:
        print("\n[Teams SIMULATION] Would POST to: {}".format(
            Config.TEAMS_WEBHOOK_URL or "<TEAMS_WEBHOOK_URL not set>"))
        print(json.dumps(payload, indent=2, default=str))
        print("[Teams SIMULATION] End\n")
        return
    # --- Real send -----------------------------------------------------------
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        Config.TEAMS_WEBHOOK_URL, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status != 200:
            raise RuntimeError("Teams webhook returned HTTP {}".format(resp.status))
