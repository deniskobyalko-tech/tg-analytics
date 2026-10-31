"""Tests for topic-based similarity service."""

from app.services.similarity import compute_topic_similarity


def test_similar_categories_high_score():
    score = compute_topic_similarity(
        title_a="Marketing Tips",
        desc_a="Digital marketing and SMM strategies",
        title_b="SMM Guide",
        desc_b="Social media marketing for business",
    )
    assert score > 0.1


def test_different_categories_low_score():
    score = compute_topic_similarity(
        title_a="Python Dev",
        desc_a="Programming tutorials and code",
        title_b="Cooking Channel",
        desc_b="Recipes and food reviews",
    )
    assert score < 0.2


def test_identical_channels_max_score():
    score = compute_topic_similarity(
        title_a="Tech News",
        desc_a="Latest technology news",
        title_b="Tech News",
        desc_b="Latest technology news",
    )
    assert score == 1.0


def test_empty_descriptions():
    score = compute_topic_similarity(
        title_a="Marketing",
        desc_a=None,
        title_b="Marketing",
        desc_b=None,
    )
    assert score == 1.0


def test_no_overlap_returns_zero():
    score = compute_topic_similarity(
        title_a="AAA",
        desc_a="BBB CCC",
        title_b="DDD",
        desc_b="EEE FFF",
    )
    assert score == 0.0
