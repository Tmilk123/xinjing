from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="XJ_")

    app_name: str = "Xinjing Backend API"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/xinjing?charset=utf8mb4"

    jwt_secret_key: str = "13859643988"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
