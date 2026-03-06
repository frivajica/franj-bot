import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.models.chat import ChatRequest, RefreshRequest
from app.services.llm_service import (fetch_resume_context,
                                      generate_system_prompt, stream_chat)

# Basic memory cache for the resume to avoid hitting Google Drive on every request
_resume_cache = None

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    global _resume_cache
    try:
        settings = get_settings()
        logger.info("Fetching resume from Google Drive...")
        _resume_cache = await fetch_resume_context(settings.RESUME_GDRIVE_URL)
        logger.info("Resume loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load resume: {e}")
    yield


router = APIRouter(lifespan=lifespan)


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=422, detail="Messages array cannot be empty.")

    global _resume_cache
    if not _resume_cache:
        # Fallback in case startup failed, try fetching again
        try:
            settings = get_settings()
            _resume_cache = await fetch_resume_context(settings.RESUME_GDRIVE_URL)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Failed to load resume context. Please try again later.",
            )

    system_prompt = generate_system_prompt(
        _resume_cache, context_language=request.language or "en"
    )

    # Convert Pydantic models back to dictionaries for LiteLLM
    messages_dicts = [
        {"role": msg.role, "content": msg.content} for msg in request.messages
    ]

    return StreamingResponse(
        stream_chat(messages_dicts, system_prompt), media_type="text/event-stream"
    )


@router.post("/refresh-resume")
async def refresh_resume(request: RefreshRequest | None = None):
    """Forces the backend to re-download the resume from Google Drive."""
    global _resume_cache
    try:
        if request and request.content:
            logger.info("Updating resume from provided payload...")
            _resume_cache = request.content
            return {"status": "success", "message": "Resume context updated from payload."}

        settings = get_settings()
        logger.info("Manually refreshing resume from Google Drive...")
        _resume_cache = await fetch_resume_context(settings.RESUME_GDRIVE_URL)
        return {"status": "success", "message": "Resume context refreshed successfully."}
    except Exception as e:
        logger.error(f"Failed to refresh resume: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh resume context: {e}",
        )
