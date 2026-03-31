from sqlalchemy import inspect
from app.models.channel import Channel
from app.models.post import Post
from app.models.category import ChannelCategory
from app.models.similarity import ChannelSimilarity, AudienceOverlap
from app.models.alert import AnomalyAlert
from app.models.benchmark import CategoryBenchmark
from app.core.database import Base


def test_channel_model_columns():
    mapper = inspect(Channel)
    columns = {c.key for c in mapper.columns}
    assert "username" in columns
    assert "subscribers_count" in columns
    assert "er" in columns
    assert "updated_at" in columns
    assert "is_tracked" in columns
    assert "status" in columns
    assert "last_telethon_at" in columns


def test_post_model_columns():
    mapper = inspect(Post)
    columns = {c.key for c in mapper.columns}
    assert "telegram_post_id" in columns
    assert "is_ad" in columns
    assert "ad_price" in columns
    assert "comments_count" in columns
    assert "fwd_from_channel" in columns


def test_all_models_registered():
    table_names = {t.name for t in Base.metadata.tables.values()}
    assert "channels" in table_names
    assert "posts" in table_names
    assert "channel_snapshots" in table_names
    assert "channel_categories" in table_names
    assert "channel_similarities" in table_names
    assert "audience_overlaps" in table_names
    assert "anomaly_alerts" in table_names
    assert "category_benchmarks" in table_names
