"""
models.py — Pydantic schemas shared across the application.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    WARNING = "Warning"
    INFO = "Info"


class NotificationIn(BaseModel):
    """Payload accepted by POST /notifications."""

    type: NotificationType = Field(
        ...,
        alias="Type",
        description="'Warning' is forwarded; 'Info' is stored only.",
    )
    name: str = Field(..., alias="Name", min_length=1)
    description: str = Field(..., alias="Description")
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="Metadata")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class NotificationRecord(BaseModel):
    """Full record as stored in memory and returned by GET endpoints."""

    id: UUID
    type: NotificationType
    name: str
    description: str
    metadata: Dict[str, Any]
    received_at: datetime
    forwarded_to_teams: bool
    forwarded_via_email: bool
    forwarded_via_slack: bool

    class Config:
        use_enum_values = True


class NotificationCreatedResponse(BaseModel):
    id: UUID
    forwarded_to_teams: bool
    forwarded_via_email: bool
    forwarded_via_slack: bool
    message: str
