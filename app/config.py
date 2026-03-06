from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://api.minimax.chat/v1"
    LLM_MODEL: str = "hosted_vllm/minimax_m2.5"
    RESUME_GDRIVE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
