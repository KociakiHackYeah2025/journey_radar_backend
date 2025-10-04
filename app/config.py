from pydantic_settings import BaseSettings  # <- zmieniono import

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
