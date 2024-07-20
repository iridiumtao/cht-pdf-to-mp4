from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_key: str

    class Config:
        env_file = ".env"
