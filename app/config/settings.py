from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_PORT: int = 8000
    MONGODB_URL: str
    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()