"""Tests for CSV export endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_export_not_found():
    resp = client.get("/api/channels/nonexistent_xyz/export?format=csv")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()
