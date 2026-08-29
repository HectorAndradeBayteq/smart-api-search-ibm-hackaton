"""Enriquecimiento de operaciones OpenAPI mediante LLM.

Implementa ``enrich_operation()`` que genera un texto descriptivo de la
operación en inglés, de 250–400 palabras, con la estructura requerida
(AC-002, AC-003, ADR-006).

Cuando ``no_enrich=True``, devuelve texto compuesto de los metadatos sin
llamar al LLM (AC-003).
"""

from __future__ import annotations

from typing import cast

import openai as _openai

#: Prompt de sistema para el enriquecimiento LLM.
_SYSTEM_PROMPT = (
    "You are a technical writer specializing in API documentation. "
    "Generate a descriptive text of 250-400 words in English for the given API operation. "
    "Include: purpose, capabilities, use cases, a 'Keywords:' line, "
    "and an 'Example questions users might ask:' section."
)


def enrich_operation(op: dict[str, object], no_enrich: bool = False) -> str:
    """Genera texto enriquecido para una operación OpenAPI.

    Si ``no_enrich=True``, compone el texto a partir de los metadatos del spec
    sin llamar al LLM. Si ``no_enrich=False``, llama a la OpenAI Responses API.

    Args:
        op: Diccionario de operación con campos de metadatos del spec.
        no_enrich: Si ``True``, omite la llamada al LLM (AC-003).

    Returns:
        Texto enriquecido en inglés (250–400 palabras) o texto de metadatos.
    """
    if no_enrich:
        return _build_metadata_text(op)

    return _call_llm(op)


def _build_metadata_text(op: dict[str, object]) -> str:
    """Compone texto simple a partir de los metadatos del spec."""
    tags = cast(list[object], op.get("tags") or [])
    parts = [
        f"API: {op.get('api_title', '')}",
        f"Version: {op.get('api_version', '')}",
        f"Operation: {op.get('method', '')} {op.get('path', '')}",
        f"Summary: {op.get('summary', '')}",
        f"Description: {op.get('description', '')}",
        f"Tags: {', '.join(str(t) for t in tags)}",
    ]
    return "\n".join(p for p in parts if p.split(": ", 1)[-1].strip())


def _call_llm(op: dict[str, object]) -> str:
    """Llama a la OpenAI Responses API y devuelve el texto enriquecido."""
    tags = cast(list[object], op.get("tags") or [])
    tags_str = ", ".join(str(t) for t in tags)
    method = str(op.get("method") or "").upper()
    user_content = (
        f"API: {op.get('api_title', '')} v{op.get('api_version', '')}\n"
        f"Operation: {method} {op.get('path', '')}\n"
        f"Summary: {op.get('summary', '')}\n"
        f"Description: {op.get('description', '')}\n"
        f"Tags: {tags_str}\n"
        f"Category: {op.get('category', '')}"
    )

    response = _openai.responses.create(
        model="gpt-4o-mini",
        input=user_content,
        instructions=_SYSTEM_PROMPT,
    )
    return str(response.output_text)
