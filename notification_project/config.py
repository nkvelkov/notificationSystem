"""
config.py — All configuration read from environment variables.
Change behaviour by setting env vars; no code changes needed.
"""

import os


class Config:
    # Microsoft Teams
    TEAMS_WEBHOOK_URL: str = os.environ.get("TEAMS_WEBHOOK_URL", "")

    # Slack
    SLACK_WEBHOOK_URL: str = os.environ.get("SLACK_WEBHOOK_URL", "")

    # Email / SMTP
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER: str = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "notifications@example.com")
    EMAIL_TO: str = os.environ.get("EMAIL_TO", "ops-team@example.com")

    # Set SIMULATION_MODE=false in production to actually send
    SIMULATION_MODE: bool = os.environ.get("SIMULATION_MODE", "false").lower() != "false"
