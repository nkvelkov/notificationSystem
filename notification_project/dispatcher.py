"""
dispatcher.py — Decides which notifiers to invoke for a given notification.

This is the only file that needs to change when adding a new channel
(e.g. Slack, PagerDuty). Everything else stays untouched.
"""

from models import NotificationRecord, NotificationType
from notifiers import teams, email, slack


def dispatch(record: NotificationRecord):
    """
    Forward the record to all appropriate channels.
    Returns (forwarded_to_teams, forwarded_via_email, forwarded_to_slack).
    A failure in one channel does NOT block the others.
    """
    teams_ok = False
    email_ok = False
    slack_ok = False

    if record.type == NotificationType.WARNING:
        try:
            teams.send(record)
            teams_ok = True
        except Exception as exc:
            print("[Teams ERROR] {}".format(exc))

        try:
            email.send(record)
            email_ok = True
        except Exception as exc:
            print("[Email ERROR] {}".format(exc))

        try:
            slack.send(record)
            slack_ok = True
        except Exception as exc:
            print("[Slack ERROR] {}".format(exc))

    return teams_ok, email_ok, slack_ok
