"""Tests for compare API endpoint."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_compare_empty_channels():
    resp = client.get("/api/compare?channels=")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False


def test_compare_single_channel():
    resp = client.get("/api/compare?channels=onlyone")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "2-4" in body["error"]


def test_compare_too_many():
    resp = client.get("/api/compare?channels=a,b,c,d,e")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "2-4" in body["error"]


@patch("app.api.compare.fetch_channel_posts", new_callable=AsyncMock, return_value=[])
@patch("app.api.compare.fetch_channel_preview", new_callable=AsyncMock)
def test_compare_not_found(mock_preview, mock_posts):
    """Channels that don't exist on Telegram return error."""
    mock_preview.return_value = {"title": None, "description": None, "avatar_url": None, "subscribers_count": 0}
    resp = client.get("/api/compare?channels=fakechannel1,fakechannel2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "не найдены" in body["error"].lower() or "not found" in body["error"].lower()
