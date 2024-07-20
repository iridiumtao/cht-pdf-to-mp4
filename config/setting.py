from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_key: str = "xxxxx"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    base_settings = Settings()
    return base_settings
