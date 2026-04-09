from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "News Radar"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./news_radar.db"

    model_config = {"env_file": ".env", "env_prefix": "NR_"}


settings = Settings()
