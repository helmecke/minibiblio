from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="MINIBIBLIO_")

    app_name: str = "MiniBiblio API"
    debug: bool = True
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    password_salt: str = "minibiblio-demo-salt"


settings = Settings()
