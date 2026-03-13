from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Grocery Goblin API"
    app_env: str = "development"
    app_version: str = "0.1.0"


settings = Settings()
