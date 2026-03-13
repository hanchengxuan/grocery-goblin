from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Grocery Goblin API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    app_port: int = 8000
    database_url: str = "postgresql://postgres:postgres@localhost:5432/grocery_goblin"
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
