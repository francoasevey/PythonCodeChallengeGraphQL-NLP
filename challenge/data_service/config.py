from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    csv_path: str = "/data/dataset.csv"
    anthropic_api_key: str
    secret_key: str
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
