"""Tests for extended stats models."""


def test_channel_member_columns():
    from app.models.member import ChannelMember
    cols = {c.name for c in ChannelMember.__table__.columns}
    assert {"id", "channel_id", "telegram_user_id", "username", "first_name", "joined_at", "left_at"} <= cols


def test_admin_log_columns():
    from app.models.admin_log import ChannelAdminLog
    cols = {c.name for c in ChannelAdminLog.__table__.columns}
    assert {"id", "channel_id", "event_type", "user_id", "data", "event_date"} <= cols


def test_invite_link_columns():
    from app.models.invite_link import ChannelInviteLink
    cols = {c.name for c in ChannelInviteLink.__table__.columns}
    assert {"id", "channel_id", "link", "creator_id", "usage_count", "fetched_at"} <= cols


def test_post_extended_columns():
    from app.models.post import Post
    cols = {c.name for c in Post.__table__.columns}
    assert {"replies_count", "saves_count", "reactions_detail"} <= cols


def test_channel_extended_columns():
    from app.models.channel import Channel
    cols = {c.name for c in Channel.__table__.columns}
    assert {"bot_is_admin", "extended_fetched_at"} <= cols
