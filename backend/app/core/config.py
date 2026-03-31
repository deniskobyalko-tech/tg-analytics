from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    POSTGRES_USER: str = "tganalytics"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "tganalytics"
    DATABASE_URL: str = "postgresql+asyncpg://tganalytics:changeme@localhost:5432/tganalytics"
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_PHONE: str = ""
    SCRAPE_INTERVAL_HOURS: int = 6
    TELETHON_INTERVAL_HOURS: int = 12
    TELETHON_ENABLED: bool = True
    CACHE_TTL_MINUTES: int = 60
    MAX_TRACKED_CHANNELS: int = 50
    ANALYSIS_QUEUE_MAX_CONCURRENT: int = 3
    ALERT_TELEGRAM_BOT_TOKEN: str = ""
    ALERT_TELEGRAM_CHAT_ID: str = ""


settings = Settings()
