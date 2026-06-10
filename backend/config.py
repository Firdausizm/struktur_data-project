from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Konfigurasi aplikasi — dimuat dari file .env"""

    GOOGLE_BOOKS_API_KEY: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "firstwebdatabase"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
