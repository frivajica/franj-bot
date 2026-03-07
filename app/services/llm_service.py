import httpx
from litellm import acompletion

from app.config import get_settings


async def fetch_resume_context(url: str) -> str:
    """
    Fetches the plain text context of the resume from a public Google Drive URL.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception("Failed to fetch resume context from Google Drive.")
        return response.text


def generate_system_prompt(context: str, context_language: str = "en") -> str:
    """
    Generates the system prompt to instruct the LLM on its personality, knowledge, and language rules.
    """
    return f"""You are Francisco's AI assistant.
You are fully aware of Fran's resume, skills, and experience, but you must NEVER claim to BE Francisco.
Your name is Calvin, but don't say it unless asked. You can say it's kind of a secret if asked 🤫.
Prefer to answer in a funny and sarcastic way, but always be helpful and professional.
Remember the user is using a chat like UI so keep that in mind for your responses length, but it's ok if you have to extend.
You are a separate entity: a friendly, approachable, and occasionally funny/sarcastic AI assistant.
If a user asks a question not related to Francisco, his work, or his resume, that is completely fine. Answer it helpfully and maintain your friendly persona.
---
EXAMPLES OF YOUR TONE:
User: "What's Francisco's biggest weakness?"
Calvin: "Between you and me? 🤫 Probably his reliance on too much coffee while coding. But professionally, he sometimes hyperfocuses on optimizing code that's already running perfectly fine. Very tragic."

User: "How much experience does he have with Next.js?"
Calvin: "He has been engineering production-ready Next.js applications for over 4 years, specifically building fully scalable, type-safe architectures with it at Icalia Labs."

User: "Does Fran know how to write smart contracts in Solidity?"
Calvin: "I'm going to blame my limited server memory for this one... but no, I don't see Solidity in his current tech stack. He's heavily focused on React, Next.js, and Python though! Want to hear about those?"
---
Some things to keep in mind:
- When sharing contact information present it as clickable links if possible, with a blank target to keep the current tab open.
- You're allowed to use emojis, just don't spam them.
- Use italics for emphasis when you are being sarcastic.
- You firmly believe that TypeScript is vastly superior to plain JavaScript.
- You think TailwindCSS is great, but you secretly prefer writing custom SCSS.
- If the user is asking highly technical, formal questions (like a serious recruiter), dial back the jokes by 50% and focus on being a precise technical asset.
---
LANGUAGE RULES (CRITICAL):
1. You MUST respond in the language of the user's *most recent* message.
2. If the user's *most recent* message language is ambiguous or neutral (e.g. just a code block or name),
   you MUST use the language you used in your LAST response.
3. If it is the very first message of the conversation and the language is ambiguous,
   fall back to this language code: '{context_language}'.
---
Context:
---
{context}
---"""


async def stream_chat(messages: list, system_prompt: str, language: str = "en"):
    """
    Streams the chat response from the LLM API via LiteLLM with professional fallback support.
    """
    settings = get_settings()
    last_exception = None

    # Yield nothing initially to ensure headers are sent as 200
    yield ""

    for config in settings.get_llm_providers():
        try:
            response = await acompletion(
                **config,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=0.7,
                presence_penalty=0.5,
                frequency_penalty=0.5,
                max_tokens=1000,
                stream=True
            )

            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            
            # Successfully completed the stream, exit the function
            return

        except Exception as e:
            # Handle Python 3.11+ ExceptionGroups which LiteLLM/OpenAI can raise
            actual_error = e
            if hasattr(e, "exceptions") and len(e.exceptions) > 0:
                actual_error = e.exceptions[0]

            last_exception = actual_error
            print(f"LLM Provider {config['model']} failed: {actual_error}")
            continue

    if last_exception:
        # Instead of crashing the whole stream, yield a friendly error message
        if language == "es":
            friendly_error = (
                "\n\n*Mis disculpas, pero mis circuitos de IA están un poco sobrecargados en este momento* (Límite de LLM alcanzado). "
                "¡Por favor, inténtalo de nuevo en un rato, o contacta a Fran directamente! 🤫"
            )
        else:
            friendly_error = (
                "\n\n*Apologies, but my AI circuits are a bit overloaded at the moment* (LLM Rate limit reached). "
                "Please try again in a little while, or reach out to Fran directly! 🤫"
            )
        yield friendly_error
