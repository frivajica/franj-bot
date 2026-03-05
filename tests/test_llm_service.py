import pytest
import respx

from app.services.llm_service import (fetch_resume_context,
                                      generate_system_prompt)


@pytest.mark.asyncio
@respx.mock
async def test_fetch_resume_context_success():
    """Test that the service correctly fetches the document from Google Drive."""
    mock_url = "https://docs.google.com/document/d/fake_id/export?format=txt"
    mock_content = "This is Fran's Resume."

    # Mock the HTTP GET request
    respx.get(mock_url).respond(status_code=200, text=mock_content)

    content = await fetch_resume_context(mock_url)
    assert content == mock_content


@pytest.mark.asyncio
@respx.mock
async def test_fetch_resume_context_failure():
    """Test graceful failure if the resume cannot be fetched."""
    mock_url = "https://docs.google.com/document/d/fake_id/export?format=txt"

    respx.get(mock_url).respond(status_code=404)

    with pytest.raises(Exception, match="Failed to fetch resume context"):
        await fetch_resume_context(mock_url)


def test_generate_system_prompt():
    """Test that the system prompt injects the context properly."""
    context = "I am a Senior Frontend Developer."
    prompt = generate_system_prompt(context, context_language="es")

    assert "You are Francisco Jimenez Casillas" in prompt
    assert context in prompt
    assert "fall back to this language code: 'es'" in prompt
