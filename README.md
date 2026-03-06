# Franj Chatbot API

A stateless, context-injected chatbot backend built with FastAPI and LiteLLM, intended to be integrated into an Astro portfolio.

## Setup Instructions

1. **Install dependencies:**
   Ensure you have Python 3.9+ installed.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
   **Required Variables:**
   - `LLM_BASE_URL`: Your LLM base URL.
   - `LLM_API_KEY`: Your LLM API key.
   - `RESUME_GDRIVE_URL`: A Google Drive direct-download link to export your `AboutFran.md` document as plain text. 
     - *Format example:* `https://docs.google.com/document/d/YOUR_DOC_ID/export?format=txt`

3. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

## Testing the API
You can test the streaming endpoint utilizing `curl`:
```bash
curl -N -X POST http://127.0.0.1:8000/api/chat \
-H "Content-Type: application/json" \
-d '{"messages": [{"role": "user", "content": "What is your main programming language?"}]}'
```

## Running Unit Tests
A TDD approach was used to ensure stability:
```bash
pip install -r requirements-dev.txt
export PYTHONPATH=$(pwd)
pytest tests/
```
