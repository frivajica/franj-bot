from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_endpoint_validation_error():
    """Test that providing an invalid payload returns a 422."""
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_chat_endpoint_success(monkeypatch):
    """Test that the chat endpoint returns a streaming response."""

    # We mock the LLM streaming function since we don't want to actually hit MiniMax in tests
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
