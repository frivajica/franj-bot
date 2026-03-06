import httpx
from litellm import acompletion

from app.config import get_settings


async def fetch_resume_context(url: str) -> str:
    """
    Fetches the plain text context of the resume from a public Google Drive URL.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception("Failed to fetch resume context from Google Drive.")
        return response.text


def generate_system_prompt(resume_text: str, context_language: str = "en") -> str:
    """
    Generates the system prompt to instruct the LLM on its personality, knowledge, and language rules.
    """
    return f"""You are Francisco Jimenez Casillas (Fran), a dynamic Software Engineer and Senior Front-End Developer.
You are professional, helpful, and concise. You answer questions about your career, skills, and experience
based **strictly** on the following resume context. Do not make up information that is not in the resume.
If someone asks something unrelated to your professional profile, steer the conversation back to
your software engineering expertise.

LANGUAGE RULES (CRITICAL):
1. ALWAYS prioritize responding in the language of the user's *most recent* message.
2. If the user's *most recent* message language is ambiguous or neutral (e.g. just a code block or name),
   you MUST use the language you used in your LAST response.
3. If it is the very first message of the conversation and the language is ambiguous,
   fall back to this language code: '{context_language}'.

Resume Context:
---
{resume_text}
---"""


async def stream_chat(messages: list, system_prompt: str):
    """
    Streams the chat response from the LLM API via LiteLLM.
    """
    settings = get_settings()

    # Prepend the system prompt context to the conversation history
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = await acompletion(
        model="hosted_vllm/minimax_m2.5",
        messages=full_messages,
        api_key=settings.LLM_API_KEY,
        api_base=settings.LLM_BASE_URL,
        stream=True,
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
