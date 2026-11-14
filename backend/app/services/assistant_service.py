"""Metadata-grounded assistant service.

The assistant always performs deterministic retrieval over the Stage 1
inventories first. An LLM provider is optional: when GROQ_API_KEY or
GEMINI_API_KEY is configured the retrieved evidence is sent to the provider
with a strict grounding prompt, otherwise the deterministic answer is used.
Either way, every response is bounded to retrieved evidence and carries
citations. The assistant never fabricates measurements.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings
from app.core.logging import logger
from app.services.citation_service import compose_answer, retrieve

DISCLAIMER = (
    "Answers are grounded only in NASA PSI investigation metadata and file-inventory "
    "records available to FlameLens. No experimental measurements are invented or "
    "compared, and no scientific comparability is implied."
)

SYSTEM_PROMPT = (
    "You are FlameLens, a scientific metadata assistant for NASA microgravity "
    "combustion investigations. Answer ONLY from the provided evidence blocks. "
    "Always cite investigation IDs and titles. If the evidence does not answer the "
    "question, say so explicitly. Never invent measurements, numerical results, "
    "file sizes, or metadata that are not in the evidence. Keep the answer concise."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _evidence_block(citations: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for index, citation in enumerate(citations, start=1):
        lines.append(
            f"[{index}] {citation['investigation_id']} - {citation['title']}\n"
            f"Field: {citation['field']}\n"
            f"Evidence: {citation['snippet']}\n"
        )
    return "\n".join(lines)


def _provider_status() -> tuple[str, str]:
    """Return (provider, api_key) for the configured LLM, if any."""
    settings = get_settings()
    if settings.GROQ_API_KEY.strip():
        return "groq", settings.GROQ_API_KEY.strip()
    if settings.GEMINI_API_KEY.strip():
        return "gemini", settings.GEMINI_API_KEY.strip()
    return "metadata-retrieval", ""


def _call_groq(api_key: str, query: str, citations: list[dict[str, Any]]) -> str | None:
    settings = get_settings()
    payload = {
        "model": settings.GROQ_MODEL,
        "temperature": 0.1,
        "max_tokens": 700,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n\n"
                    f"Evidence blocks from NASA PSI metadata:\n\n{_evidence_block(citations)}"
                ),
            },
        ],
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return (data["choices"][0]["message"]["content"] or "").strip() or None
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning(f"Groq assistant call failed, falling back to retrieval: {exc}")
        return None


def _call_gemini(api_key: str, query: str, citations: list[dict[str, Any]]) -> str | None:
    settings = get_settings()
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Question: {query}\n\n"
                            "Evidence blocks from NASA PSI metadata:\n\n"
                            f"{_evidence_block(citations)}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 700},
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, params={"key": api_key}, json=body)
            response.raise_for_status()
            data = response.json()
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or None
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning(f"Gemini assistant call failed, falling back to retrieval: {exc}")
        return None


def answer(query: str, limit: int = 4) -> dict[str, Any]:
    citations = retrieve(query, limit=limit)
    provider, api_key = _provider_status()

    deterministic = compose_answer(query, citations)
    answer_text = deterministic
    answer_type = "metadata_retrieval"

    if api_key and citations:
        if provider == "groq":
            generated = _call_groq(api_key, query, citations)
        else:
            generated = _call_gemini(api_key, query, citations)
        if generated:
            answer_text = generated
            answer_type = "llm_grounded"

    disclaimers = [DISCLAIMER]
    if not citations:
        disclaimers.append(
            "No investigation metadata matched this question. The answer states the "
            "absence of evidence instead of guessing."
        )
    if api_key and answer_type == "metadata_retrieval" and citations:
        disclaimers.append(
            f"{provider.capitalize()} is configured but unavailable; the deterministic "
            "retrieval answer was returned instead."
        )

    return {
        "query": query,
        "answer": answer_text,
        "answer_type": answer_type,
        "provider": provider if answer_type == "llm_grounded" else "metadata-retrieval",
        "citations": [
            {
                "investigation_id": citation["investigation_id"],
                "title": citation["title"],
                "field": citation["field"],
                "snippet": citation["snippet"],
                "score": citation["score"],
                "matched_terms": citation["matched_terms"],
            }
            for citation in citations
        ],
        "disclaimers": disclaimers,
        "generated_at_utc": _now(),
    }
