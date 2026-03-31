from app.services.scraper import parse_tme_preview, parse_tme_posts

SAMPLE_HTML = """
<html>
<head>
<meta property="og:title" content="Test Channel">
<meta property="og:description" content="A test channel description">
<meta property="og:image" content="https://cdn.telegram.org/avatar.jpg">
</head>
<body>
<div class="tgme_page_extra">12 345 subscribers</div>
</body>
</html>
"""

SAMPLE_POSTS_HTML = """
<div class="tgme_widget_message" data-post="testchannel/123">
  <div class="tgme_widget_message_text">Hello world</div>
  <span class="tgme_widget_message_views">5.2K</span>
  <time datetime="2026-03-28T10:00:00+00:00"></time>
  <span class="tgme_widget_message_forwarded_from">Forwarded from <a>@otherchannel</a></span>
</div>
"""

def test_parse_tme_preview():
    result = parse_tme_preview(SAMPLE_HTML)
    assert result["title"] == "Test Channel"
    assert result["description"] == "A test channel description"
    assert result["avatar_url"] == "https://cdn.telegram.org/avatar.jpg"
    assert result["subscribers_count"] == 12345

def test_parse_tme_preview_missing_data():
    result = parse_tme_preview("<html><head></head><body></body></html>")
    assert result["title"] is None
    assert result["subscribers_count"] == 0

def test_parse_tme_posts():
    posts = parse_tme_posts(SAMPLE_POSTS_HTML)
    assert len(posts) == 1
    assert posts[0]["text"] == "Hello world"
    assert posts[0]["views"] == 5200
    assert posts[0]["fwd_from_channel"] == "otherchannel"
