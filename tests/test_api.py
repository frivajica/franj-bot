from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_endpoint_validation_error():
    """Test that providing an invalid payload returns a 422."""
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_chat_endpoint_success(monkeypatch):
    """Test that the chat endpoint returns a streaming response."""

    # We mock the LLM streaming function since we don't want to actually hit the LLM in tests
    async def mock_stream_chat(*args, **kwargs):
        yield "Hello "
        yield "World!"

    monkeypatch.setattr("app.api.routes.chat.stream_chat", mock_stream_chat)
    monkeypatch.setattr("app.api.routes.chat._resume_cache", "Mocked resume context")

    response = client.post(
        "/api/chat", json={"messages": [{"role": "user", "content": "Hi there!"}]}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    assert response.text == "Hello World!"


def test_refresh_resume_success(monkeypatch):
    """Test that the refresh endpoint successfully updates the cache."""
    # Mock the fetch function to simulate a successful Google Drive download
    async def mock_fetch_success(*args, **kwargs):
        return "New fresh resume context"

    monkeypatch.setattr("app.api.routes.chat.fetch_resume_context", mock_fetch_success)

    response = client.post("/api/refresh-resume")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Resume context refreshed successfully.",
    }


def test_refresh_resume_failure(monkeypatch):
    """Test that the refresh endpoint handles errors gracefully."""
    # Mock the fetch function to simulate a network error
    async def mock_fetch_failure(*args, **kwargs):
        raise Exception("Google Drive is down")

    monkeypatch.setattr("app.api.routes.chat.fetch_resume_context", mock_fetch_failure)

    response = client.post("/api/refresh-resume")

    assert response.status_code == 500
    assert "Failed to refresh resume context" in response.json()["detail"]


def test_refresh_resume_with_payload():
    """Test that the refresh endpoint updates the cache from the payload."""
    response = client.post("/api/refresh-resume", json={"content": "Direct payload content"})
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Resume context updated from payload.",
    }
    
    # Verify it updated the cache
    from app.api.routes.chat import _resume_cache
    assert _resume_cache == "Direct payload content"
