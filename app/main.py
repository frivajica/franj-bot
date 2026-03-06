from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router

app = FastAPI(title="Franj Chatbot API")

# Setup CORS to allow Astro to communicate with the service
# Hardcoding common Astro development ports, and allowing all for production deploy simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "https://franj.dev",
    ],  # Adjust '*' in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
@app.head("/")
def root():
    return {"status": "healthy", "service": "franj-chatbot-api"}
