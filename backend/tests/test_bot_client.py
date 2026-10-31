"""Tests for bot client service."""

from app.services.bot_client import parse_reactions_detail


def test_parse_reactions_detail():
    reactions = [
        {"type": "emoji", "emoji": "\ud83d\udc4d", "total_count": 15},
        {"type": "emoji", "emoji": "\u2764\ufe0f", "total_count": 8},
    ]
    result = parse_reactions_detail(reactions)
    assert result == {"\ud83d\udc4d": 15, "\u2764\ufe0f": 8}


def test_parse_reactions_detail_empty():
    assert parse_reactions_detail([]) == {}


def test_parse_reactions_detail_none():
    assert parse_reactions_detail(None) == {}
