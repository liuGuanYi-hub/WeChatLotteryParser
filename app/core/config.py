from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """纯名单抽奖器的运行配置。"""

    app_name: str = "简易抽奖器"
    app_version: str = "2.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    max_participants: int = 1000
    max_winners: int = 1000
    max_draw_count: int = 100
    storage_path: str = "data/lottery.sqlite3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
