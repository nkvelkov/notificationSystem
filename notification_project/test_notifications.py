"""
test_notifications.py

Run from inside notification_project/:
    python -m pytest test_notifications.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient

import store
from main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture()
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------------

WARNING_PAYLOAD = {
    "Type": "Warning",
    "Name": "Backup Failure",
    "Description": "The backup failed due to a database problem",
    "Metadata": {"service": "backup-agent", "host": "db-01"},
}

INFO_PAYLOAD = {
    "Type": "Info",
    "Name": "Quota Exceeded",
    "Description": "Compute Quota exceeded",
    "Metadata": {"service": "compute-monitor"},
}


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

class TestCreateNotification:
    def test_warning_returns_201(self, client):
        assert client.post("/notifications", json=WARNING_PAYLOAD).status_code == 201

    def test_info_returns_201(self, client):
        assert client.post("/notifications", json=INFO_PAYLOAD).status_code == 201

    def test_warning_forwarded_teams(self, client):
        assert client.post("/notifications", json=WARNING_PAYLOAD).json()["forwarded_to_teams"] is True

    def test_warning_forwarded_email(self, client):
        assert client.post("/notifications", json=WARNING_PAYLOAD).json()["forwarded_via_email"] is True

    def test_warning_forwarded_slack(self, client):
        assert client.post("/notifications", json=WARNING_PAYLOAD).json()["forwarded_via_slack"] is True

    def test_info_not_forwarded(self, client):
        body = client.post("/notifications", json=INFO_PAYLOAD).json()
        assert body["forwarded_to_teams"] is False
        assert body["forwarded_via_email"] is False
        assert body["forwarded_via_slack"] is False

    def test_invalid_type_422(self, client):
        assert client.post("/notifications", json=dict(WARNING_PAYLOAD, **{"Type": "Critical"})).status_code == 422

    def test_missing_name_422(self, client):
        bad = {k: v for k, v in WARNING_PAYLOAD.items() if k != "Name"}
        assert client.post("/notifications", json=bad).status_code == 422

    def test_metadata_optional(self, client):
        assert client.post("/notifications", json={"Type": "Info", "Name": "X", "Description": "Y"}).status_code == 201

    def test_multiple_services(self, client):
        for i in range(5):
            assert client.post("/notifications", json=dict(WARNING_PAYLOAD, **{"Name": "A{}".format(i)})).status_code == 201
        assert len(client.get("/notifications").json()) == 5


# ---------------------------------------------------------------------------
# GET list
# ---------------------------------------------------------------------------

class TestListNotifications:
    def _seed(self, client):
        client.post("/notifications", json=WARNING_PAYLOAD)
        client.post("/notifications", json=INFO_PAYLOAD)

    def test_all(self, client):
        self._seed(client)
        assert len(client.get("/notifications").json()) == 2

    def test_filter_warning(self, client):
        self._seed(client)
        results = client.get("/notifications?type=Warning").json()
        assert len(results) == 1 and results[0]["type"] == "Warning"

    def test_filter_info(self, client):
        self._seed(client)
        assert all(n["type"] == "Info" for n in client.get("/notifications?type=Info").json())

    def test_filter_forwarded_true(self, client):
        self._seed(client)
        results = client.get("/notifications?forwarded=true").json()
        assert all(n["forwarded_to_teams"] or n["forwarded_via_email"] or n["forwarded_via_slack"] for n in results)

    def test_filter_forwarded_false(self, client):
        self._seed(client)
        results = client.get("/notifications?forwarded=false").json()
        assert all(
            not n["forwarded_to_teams"] and not n["forwarded_via_email"] and not n["forwarded_via_slack"]
            for n in results
        )

    def test_empty(self, client):
        assert client.get("/notifications").json() == []


# ---------------------------------------------------------------------------
# GET single
# ---------------------------------------------------------------------------

class TestGetNotification:
    def test_correct_record(self, client):
        nid = client.post("/notifications", json=WARNING_PAYLOAD).json()["id"]
        body = client.get("/notifications/{}".format(nid)).json()
        assert body["id"] == nid and body["name"] == WARNING_PAYLOAD["Name"]

    def test_404(self, client):
        assert client.get("/notifications/00000000-0000-0000-0000-000000000000").status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

class TestClearNotifications:
    def test_clears(self, client):
        client.post("/notifications", json=WARNING_PAYLOAD)
        assert client.delete("/notifications").status_code == 204
        assert client.get("/notifications").json() == []
