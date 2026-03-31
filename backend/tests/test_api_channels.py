"""Tests for the channels API routes.

Uses an in-memory SQLite database (aiosqlite) so the tests run without
a real PostgreSQL instance.
"""
import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite engine for tests
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite://"  # pure in-memory

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    """Create all tables in the in-memory DB once per test module."""

    async def _create():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    yield
    # Tables remain for the module lifetime; engine is discarded after.


client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_PREVIEW = {
    "title": "Test Channel",
    "description": "Test description",
    "avatar_url": "https://example.com/avatar.jpg",
    "subscribers_count": 5000,
}

MOCK_POSTS: list[dict] = []


# ---------------------------------------------------------------------------
# Tests — POST /api/channels/analyze
# ---------------------------------------------------------------------------


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_analyze_channel(mock_preview: AsyncMock, mock_posts: AsyncMock) -> None:
    mock_preview.return_value = MOCK_PREVIEW
    mock_posts.return_value = MOCK_POSTS

    resp = client.post("/api/channels/analyze", json={"username": "@testchannel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["username"] == "testchannel"
    assert body["data"]["title"] == "Test Channel"
    assert body["data"]["subscribers_count"] == 5000


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_analyze_channel_strips_at(mock_preview: AsyncMock, mock_posts: AsyncMock) -> None:
    """Username with @ prefix must be cleaned before lookup."""
    mock_preview.return_value = MOCK_PREVIEW
    mock_posts.return_value = MOCK_POSTS

    resp = client.post("/api/channels/analyze", json={"username": "@AnotherChannel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["username"] == "anotherchannel"


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_analyze_channel_no_title_returns_error(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """When the scraper returns no title the channel is treated as not found."""
    mock_preview.return_value = {
        "title": None,
        "description": None,
        "avatar_url": None,
        "subscribers_count": 0,
    }
    mock_posts.return_value = []

    resp = client.post("/api/channels/analyze", json={"username": "privatechannel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_analyze_channel_scraper_error(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """Network / scraper errors must bubble up as success=False."""
    mock_preview.side_effect = Exception("timeout")
    mock_posts.return_value = []

    resp = client.post("/api/channels/analyze", json={"username": "brokenChannel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "Failed to fetch" in body["error"]


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_analyze_channel_with_posts(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """ER and avg_views computed correctly from mocked posts."""
    mock_preview.return_value = {**MOCK_PREVIEW, "subscribers_count": 10_000}
    mock_posts.return_value = [
        {
            "telegram_post_id": 101,
            "text": "Hello world",
            "date": "2026-03-01T12:00:00",
            "views": 2000,
            "forwards": 5,
            "reactions": 10,
            "fwd_from_channel": None,
        },
        {
            "telegram_post_id": 102,
            "text": "Another post",
            "date": "2026-03-08T12:00:00",
            "views": 3000,
            "forwards": 2,
            "reactions": 7,
            "fwd_from_channel": None,
        },
    ]

    resp = client.post("/api/channels/analyze", json={"username": "postyChannel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    # avg_views = (2000 + 3000) / 2 = 2500
    assert body["data"]["avg_views"] == 2500
    # er = (2500 / 10000) * 100 = 25.0
    assert body["data"]["er"] == 25.0


# ---------------------------------------------------------------------------
# Tests — GET /api/channels/{username}
# ---------------------------------------------------------------------------


def test_get_channel_not_found() -> None:
    resp = client.get("/api/channels/nonexistent999")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_get_channel_after_analyze(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """After analyzing, GET should return the persisted channel."""
    mock_preview.return_value = {**MOCK_PREVIEW, "title": "Findable Channel"}
    mock_posts.return_value = []

    client.post("/api/channels/analyze", json={"username": "findablechannel"})

    resp = client.get("/api/channels/findablechannel")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["username"] == "findablechannel"
    assert body["data"]["title"] == "Findable Channel"


# ---------------------------------------------------------------------------
# Tests — GET /api/channels/{username}/history
# ---------------------------------------------------------------------------


def test_get_channel_history_not_found() -> None:
    resp = client.get("/api/channels/ghost_channel/history")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_get_channel_history_empty(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """History should return empty list when no snapshots exist."""
    mock_preview.return_value = {**MOCK_PREVIEW, "title": "History Channel"}
    mock_posts.return_value = []

    client.post("/api/channels/analyze", json={"username": "historychannel"})

    resp = client.get("/api/channels/historychannel/history?days=30")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


# ---------------------------------------------------------------------------
# Tests — GET /api/channels/{username}/posts
# ---------------------------------------------------------------------------


def test_get_channel_posts_not_found() -> None:
    resp = client.get("/api/channels/absolutely_unknown/posts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


@patch("app.api.channels.fetch_channel_posts", new_callable=AsyncMock)
@patch("app.api.channels.fetch_channel_preview", new_callable=AsyncMock)
def test_get_channel_posts_pagination(
    mock_preview: AsyncMock, mock_posts: AsyncMock
) -> None:
    """Posts endpoint returns pagination meta."""
    mock_preview.return_value = {**MOCK_PREVIEW, "title": "Posts Channel"}
    mock_posts.return_value = [
        {
            "telegram_post_id": 200 + i,
            "text": f"Post {i}",
            "date": f"2026-03-{i + 1:02d}T10:00:00",
            "views": 100 * i,
            "forwards": 0,
            "reactions": 0,
            "fwd_from_channel": None,
        }
        for i in range(1, 6)  # 5 posts
    ]

    client.post("/api/channels/analyze", json={"username": "postschannel"})

    resp = client.get("/api/channels/postschannel/posts?page=1&limit=3")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["meta"]["total"] == 5
    assert body["meta"]["page"] == 1
    assert body["meta"]["limit"] == 3
    assert len(body["data"]) == 3
