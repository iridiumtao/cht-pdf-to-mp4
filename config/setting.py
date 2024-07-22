from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    vision_key: str
    vision_endpoint: str
    speech_key: str
    speech_region: str

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    base_settings = Settings()
    return base_settings
