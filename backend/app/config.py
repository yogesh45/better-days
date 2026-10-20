from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://betterdays:betterdays_dev_password@localhost:5432/betterdays"
    jwt_secret: str = "dev-only-change-me-before-deployment"
    jwt_exp_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:3000,http://localhost:8081"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
