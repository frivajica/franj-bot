import pytest
from pydantic import ValidationError

# We run this test assuming `app.config` will have a `Settings` class
# that loads environment variables.


def test_settings_load_successfully(monkeypatch):
    """Test that valid environment variables load into the Settings object successfully."""
    monkeypatch.setenv("LLM_API_KEY", "test_key_123")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.minimax.chat/v1")
    monkeypatch.setenv(
        "RESUME_GDRIVE_URL",
        "https://docs.google.com/document/d/some_id/export?format=txt",
    )

    from app.config import get_settings

    settings = get_settings()

    assert settings.LLM_API_KEY == "test_key_123"
    assert settings.LLM_BASE_URL == "https://api.minimax.chat/v1"
    assert (
        settings.RESUME_GDRIVE_URL
        == "https://docs.google.com/document/d/some_id/export?format=txt"
    )


def test_settings_missing_required_vars(monkeypatch):
    """Test that missing required keys raise a ValidationError immediately."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    from app.config import Settings

    with pytest.raises(ValidationError):
        # Initializing without the required LLM_API_KEY should fail
        # We pass _env_file=None to ensure it doesn't pick up the local .env file
        Settings(_env_file=None)
