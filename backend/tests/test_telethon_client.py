from app.services.telethon_client import extract_channel_stats, extract_post_data

def test_extract_channel_stats():
    mock_entity = type("Entity", (), {
        "id": 123456789,
        "title": "Test Channel",
        "username": "testchannel",
        "participants_count": 5000,
    })()
    stats = extract_channel_stats(mock_entity)
    assert stats["telegram_id"] == 123456789
    assert stats["subscribers_count"] == 5000
    assert stats["title"] == "Test Channel"

def test_extract_post_data():
    mock_msg = type("Message", (), {
        "id": 42,
        "message": "Hello world",
        "date": "2026-03-30T10:00:00",
        "views": 1500,
        "forwards": 30,
        "reactions": None,
    })()
    post = extract_post_data(mock_msg)
    assert post["telegram_post_id"] == 42
    assert post["views"] == 1500
    assert post["reactions"] == 0
