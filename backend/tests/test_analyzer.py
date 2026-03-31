from app.services.analyzer import calculate_er, detect_ad_post

def test_calculate_er():
    assert calculate_er(avg_views=500, subscribers=1000) == 50.0

def test_calculate_er_zero_subscribers():
    assert calculate_er(avg_views=100, subscribers=0) == 0.0

def test_detect_ad_post_keyword():
    assert detect_ad_post("Реклама. Подписывайтесь на @channel") is True

def test_detect_ad_post_utm():
    assert detect_ad_post("Ссылка: https://example.com?utm_source=tg") is True

def test_detect_ad_post_clean():
    assert detect_ad_post("Вышла новая статья про маркетинг") is False
