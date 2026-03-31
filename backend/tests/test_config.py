from app.core.config import settings


def test_settings_loads():
    assert settings.POSTGRES_USER is not None
    assert settings.CACHE_TTL_MINUTES == 60
