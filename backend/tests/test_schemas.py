from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.channel import ChannelOut, ChannelAnalyzeRequest


def test_api_response_success():
    resp = ApiResponse(success=True, data={"key": "value"}, error=None, meta=None)
    assert resp.success is True
    assert resp.data == {"key": "value"}


def test_channel_analyze_request_strips_at():
    req = ChannelAnalyzeRequest(username="@testchannel")
    assert req.username == "testchannel"


def test_channel_out_schema():
    data = ChannelOut(
        id=1, telegram_id=123, username="test", title="Test",
        subscribers_count=1000, avg_views=500, er=50.0, posts_per_week=7.0,
    )
    assert data.er == 50.0
