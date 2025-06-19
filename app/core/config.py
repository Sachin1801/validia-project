from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application configuration leveraging environment variables."""

    app_name: str = "Validia"
    api_v1_prefix: str = "/v1"

    class Config:
        env_file = ".env"


settings = Settings()
