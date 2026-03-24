from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    client_id: str
    client_secret: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
