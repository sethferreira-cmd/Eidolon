from fastapi import APIRouter
from providers import ollama as ollama_provider

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/models")
def models():
    conn_status = ollama_provider.check_connection()
    if not conn_status.get("available"):
        return {
            "ollama_available": False,
            "models": [],
            "demo_mode_recommended": True,
            "error": conn_status.get("error"),
        }
    detected = ollama_provider.list_models()
    return {
        "ollama_available": True,
        "models": detected,
        "demo_mode_recommended": len(detected) == 0,
    }
