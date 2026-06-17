"""
store.py — In-memory storage for notifications.

Kept as a module-level dict so it is shared across all imports
within a single process. Swap this module for a database-backed
implementation without touching anything else.
"""

from typing import Dict
from uuid import UUID

from models import NotificationRecord

_store: Dict[UUID, NotificationRecord] = {}


def save(record: NotificationRecord) -> None:
    _store[record.id] = record


def get(notification_id: UUID):
    # type: (...) -> NotificationRecord or None
    return _store.get(notification_id)


def all_records():
    # type: () -> list
    return list(_store.values())


def clear() -> None:
    _store.clear()
