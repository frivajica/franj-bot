from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MINIMAX_API_KEY: str
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    RESUME_GDRIVE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
