"""Tests for watchlist API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_watchlist_returns_list():
    resp = client.get("/api/watchlist")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_watchlist_add_not_found():
    resp = client.post("/api/watchlist/nonexistent_channel_xyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


def test_watchlist_remove_not_found():
    resp = client.delete("/api/watchlist/nonexistent_channel_xyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
