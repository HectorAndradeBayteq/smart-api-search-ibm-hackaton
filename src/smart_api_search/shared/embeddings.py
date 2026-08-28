"""Cliente de embeddings configurable: único punto de acceso a vectorización.

Selecciona el proveedor según ``settings.EMBED_PROVIDER``:
- ``openai``: usa ``text-embedding-3-large`` truncado a ``EMBED_DIM`` dimensiones (ADR-009).
- ``watsonx``: usa ``ibm/granite-embedding-278m-multilingual`` con ``EMBED_DIM=768`` (ADR-014).

Ninguna otra capa del paquete puede importar directamente los SDKs de
embeddings; toda llamada debe pasar por ``get_embedding()`` (ADR-009, AC-025).
"""

from __future__ import annotations

from smart_api_search.config import EmbedProvider, settings

# Importaciones condicionales de SDKs: se importan en tiempo de ejecución para
# evitar errores de importación cuando el paquete no está instalado.
try:
    import openai as _openai_module

    openai = _openai_module
except ImportError:  # pragma: no cover
    openai = None  # type: ignore[assignment]

try:
    from langchain_ibm import WatsonxEmbeddings as _WatsonxEmbeddings

    WatsonxEmbeddings = _WatsonxEmbeddings
except ImportError:  # pragma: no cover
    try:
        from ibm_watsonx_ai.foundation_models import (
            Embeddings as _WxEmbeddings,
        )

        WatsonxEmbeddings = _WxEmbeddings
    except ImportError:
        WatsonxEmbeddings = None


def get_embedding(text: str) -> list[float]:
    """Genera el vector denso para ``text`` usando el proveedor configurado.

    El proveedor se lee de ``settings.EMBED_PROVIDER``; la dimensión de
    ``settings.EMBED_DIM`` nunca aparece como literal en este módulo
    (AC-027, ADR-009).

    Args:
        text: Texto a vectorizar.

    Returns:
        Vector de floats con longitud ``settings.EMBED_DIM``.

    Raises:
        RuntimeError: Si el proveedor no está soportado o el SDK no está disponible.
    """
    provider = settings.EMBED_PROVIDER

    if provider == EmbedProvider.OPENAI:
        return _embed_openai(text)
    elif provider == EmbedProvider.WATSONX:
        return _embed_watsonx(text)
    else:
        raise RuntimeError(f"Proveedor de embeddings no soportado: {provider!r}")


def _embed_openai(text: str) -> list[float]:
    """Genera embedding con OpenAI ``text-embedding-3-large`` (AC-026)."""
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text,
        dimensions=settings.EMBED_DIM,
    )
    return list(response.data[0].embedding)


def _embed_watsonx(text: str) -> list[float]:
    """Genera embedding con IBM Granite multilingual (AC-026, ADR-014)."""
    embedder = WatsonxEmbeddings(
        model_id="ibm/granite-embedding-278m-multilingual",
        url=settings.WATSONX_URL,
        apikey=settings.WATSONX_API_KEY,
        project_id=settings.WATSONX_PROJECT_ID,
    )
    return list(embedder.embed_query(text))
