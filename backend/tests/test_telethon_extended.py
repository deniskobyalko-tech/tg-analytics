"""Tests for Telethon extended methods parsing helpers."""

from datetime import datetime
from unittest.mock import MagicMock

from app.services.telethon_client import parse_admin_log_event, parse_participant


def test_parse_admin_log_join():
    event = MagicMock()
    event.date = datetime(2026, 3, 15, 10, 0, 0)
    event.user_id = 12345
    event.action.__class__.__name__ = "ChannelAdminLogEventActionParticipantJoin"

    result = parse_admin_log_event(event)
    assert result["event_type"] == "join"
    assert result["user_id"] == 12345


def test_parse_admin_log_leave():
    event = MagicMock()
    event.date = datetime(2026, 3, 16, 12, 0, 0)
    event.user_id = 999
    event.action.__class__.__name__ = "ChannelAdminLogEventActionParticipantLeave"

    result = parse_admin_log_event(event)
    assert result["event_type"] == "leave"


def test_parse_admin_log_unknown():
    event = MagicMock()
    event.date = datetime(2026, 3, 16, 12, 0, 0)
    event.user_id = 1
    event.action.__class__.__name__ = "SomeOtherAction"

    result = parse_admin_log_event(event)
    assert result["event_type"] == "SomeOtherAction"


def test_parse_participant():
    user = MagicMock()
    user.id = 999
    user.username = "testuser"
    user.first_name = "Test"

    participant = MagicMock()
    participant.date = None

    result = parse_participant(user, participant)
    assert result["telegram_user_id"] == 999
    assert result["username"] == "testuser"
    assert result["first_name"] == "Test"
    assert result["joined_at"] is None
