"""FastAPI application entrypoint for AgentForge."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.generate import router as generate_router

load_dotenv()

app = FastAPI(title="AgentForge Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return the service health status."""
    return {
        "status": "ok",
        "service": "agentforge",
        "version": "1.0.0",
    }
