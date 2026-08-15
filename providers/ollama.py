"""
Local Ollama provider.

Talks to a locally running Ollama daemon (default http://localhost:11434).
Never raises out to the caller on connectivity problems -- every method
returns a structured result so the API layer can degrade gracefully to
Demo Mode instead of crashing.
"""

import json
import os
import time
from typing import Optional

import httpx

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "60"))


class OllamaUnavailable(Exception):
    pass


def check_connection() -> dict:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{OLLAMA_HOST}/api/tags")
            resp.raise_for_status()
            return {"available": True}
    except Exception as e:  # noqa: BLE001 - deliberately broad, this is a health check
        return {"available": False, "error": str(e)}


def list_models() -> list:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{OLLAMA_HOST}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate(model: str, prompt: str, timeout: Optional[float] = None) -> dict:
    """
    Send a prompt to a local Ollama model. Returns:
      {"ok": True, "raw_response": str, "latency_ms": int}
    or
      {"ok": False, "error": str}
    Never raises.
    """
    start = time.time()
    try:
        with httpx.Client(timeout=timeout or DEFAULT_TIMEOUT) as client:
            resp = client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            latency_ms = int((time.time() - start) * 1000)
            return {
                "ok": True,
                "raw_response": data.get("response", ""),
                "latency_ms": latency_ms,
            }
    except httpx.TimeoutException:
        return {"ok": False, "error": "timeout"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"ok": False, "error": f"model not found: {model}"}
        return {"ok": False, "error": f"http error {e.response.status_code}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"connection error: {e}"}


def parse_json_response(raw_response: str) -> dict:
    """
    Attempt to extract and parse a JSON object from a raw model response.
    Models sometimes wrap JSON in markdown fences or add preamble text;
    this makes a best effort to strip that before parsing. On failure,
    returns {"parse_failed": True} and preserves the raw text -- it never
    fabricates a result.
    """
    if not raw_response or not raw_response.strip():
        return {"parse_failed": True, "reason": "empty response"}

    text = raw_response.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {"parse_failed": True, "reason": "no JSON object found"}

    candidate = text[start:end + 1]
    try:
        parsed = json.loads(candidate)
        parsed["parse_failed"] = False
        return parsed
    except json.JSONDecodeError as e:
        return {"parse_failed": True, "reason": f"json decode error: {e}"}
