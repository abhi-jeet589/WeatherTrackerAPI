from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(
        case_sensitive=True, env_ignore_empty=True, extra="ignore"
    )

    DATABASE_URL: str = Field(description="Database URL")
    DATABASE_NAME: str = Field(description="Database name")
    ECHO_SQL: bool = Field(description="Enable SQL logging", default=False)
    API_KEY: str = Field(description="API key for OpenWeatherMap API")
    API_BASE_URL: str = Field(description="URL for OpenWeatherApp API")


settings = Settings()
