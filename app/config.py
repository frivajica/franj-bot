from functools import lru_cache
from typing import Generator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LLM_API_KEY: str
    LLM_BASE_URL: str
    LLM_MODEL: str = "groq/llama-3.3-70b-versatile"
    RESUME_GDRIVE_URL: str

    FALLBACK_LLM_API_KEY: str | None = None
    FALLBACK_LLM_BASE_URL: str | None = None
    FALLBACK_LLM_MODEL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def get_llm_providers(self) -> Generator[dict, None, None]:
        """Yields active LLM configurations (Primary then Fallback)."""
        yield {
            "api_key": self.LLM_API_KEY,
            "base_url": self.LLM_BASE_URL,
            "model": self.LLM_MODEL,
        }
        if self.FALLBACK_LLM_MODEL and self.FALLBACK_LLM_API_KEY:
            yield {
                "api_key": self.FALLBACK_LLM_API_KEY,
                "base_url": self.FALLBACK_LLM_BASE_URL,
                "model": self.FALLBACK_LLM_MODEL,
            }


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
