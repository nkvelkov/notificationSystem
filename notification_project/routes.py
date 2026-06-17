"""
routes.py — FastAPI route definitions.

Imports from store, models, and dispatcher.
Here we are doing only HTTP wiring.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

import dispatcher
import store
from models import (
    NotificationCreatedResponse,
    NotificationIn,
    NotificationRecord,
    NotificationType,
)

router = APIRouter()


@router.post(
    "/notifications",
    response_model=NotificationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a notification",
    tags=["Notifications"],
)
def create_notification(body: NotificationIn) -> NotificationCreatedResponse:
    """
    - **Warning** → stored + forwarded to Teams and Email.
    - **Info**    → stored only.
    """
    record = NotificationRecord(
        id=uuid4(),
        type=body.type,
        name=body.name,
        description=body.description,
        metadata=body.metadata,
        received_at=datetime.now(tz=timezone.utc),
        forwarded_to_teams=False,
        forwarded_via_email=False,
        forwarded_via_slack=False,
    )

    teams_ok, email_ok, slack_ok = dispatcher.dispatch(record)
    record = record.copy(update={
        "forwarded_to_teams": teams_ok,
        "forwarded_via_email": email_ok,
        "forwarded_via_slack": slack_ok,
    })
    store.save(record)

    if teams_ok or email_ok or slack_ok:
        channels = " and ".join(
            (["Teams"] if teams_ok else [])
            + (["Email"] if email_ok else [])
            + (["Slack"] if slack_ok else [])
        )
        msg = "Notification received and forwarded via {}.".format(channels)
    else:
        msg = (
            "Notification received (not forwarded — Info type)."
            if record.type == NotificationType.INFO
            else "Notification received but forwarding failed."
        )

    return NotificationCreatedResponse(
        id=record.id,
        forwarded_to_teams=teams_ok,
        forwarded_via_email=email_ok,
        forwarded_via_slack=slack_ok,
        message=msg,
    )


@router.get(
    "/notifications",
    response_model=List[NotificationRecord],
    summary="List all notifications",
    tags=["Notifications"],
)
def list_notifications(
    type: Optional[NotificationType] = None,
    forwarded: Optional[bool] = None,
) -> List[NotificationRecord]:
    results = store.all_records()
    if type is not None:
        results = [r for r in results if r.type == type]
    if forwarded is not None:
        results = [
            r for r in results
            if (r.forwarded_to_teams or r.forwarded_via_email or r.forwarded_via_slack) == forwarded
        ]
    return results


@router.get(
    "/notifications/{notification_id}",
    response_model=NotificationRecord,
    summary="Get a single notification",
    tags=["Notifications"],
)
def get_notification(notification_id: UUID) -> NotificationRecord:
    record = store.get(notification_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification '{}' not found.".format(notification_id),
        )
    return record


@router.delete(
    "/notifications",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear all notifications",
    tags=["Notifications"],
)
def clear_notifications() -> None:
    store.clear()
