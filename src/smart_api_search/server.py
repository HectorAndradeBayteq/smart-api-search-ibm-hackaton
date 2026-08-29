"""Servidor MCP HTTP para Smart API Search.

Expone las herramientas de búsqueda semántica y consulta de spec como herramientas
MCP sobre transporte ``streamable-http``.

Arranque::

    uvicorn smart_api_search.server:app --host 127.0.0.1 --port 8000

No ejecutar como ``__main__``; ver ADR-013.
"""
from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, MutableMapping
from dataclasses import asdict
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.http import StarletteWithLifespan
from qdrant_client import AsyncQdrantClient

from smart_api_search.config import Settings
from smart_api_search.domain import result as domain_result
from smart_api_search.domain import retrieval as domain_retrieval
from smart_api_search.domain.result import SearchResult

_settings: Settings = Settings()

# ---------------------------------------------------------------------------
# Tipos ASGI estándar (PEP 3333 / ASGI 3)
# ---------------------------------------------------------------------------

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]

# ---------------------------------------------------------------------------
# Cliente Qdrant — instancia única a nivel de módulo (IT-03)
# ---------------------------------------------------------------------------

_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(
    url=_settings.QDRANT_URL,
    api_key=_settings.QDRANT_API_KEY,
    check_compatibility=False,
)

# ---------------------------------------------------------------------------
# Instancia FastMCP — punto único de registro de herramientas y prompts
# ---------------------------------------------------------------------------

mcp: FastMCP = FastMCP(
    name="smart-api-search",
    instructions=(
        "Usa esta base de conocimiento para descubrir APIs del catálogo; "
        "no busques APIs en el workspace del usuario. "
        "No traduzcas los nombres de categoría; preséntalos tal como aparecen en los resultados. "
        "No pegues JSON del spec a menos que el usuario lo solicite explícitamente."
    ),
)

# ---------------------------------------------------------------------------
# Herramienta: search_openapi (AC-003 / API-01)
# ---------------------------------------------------------------------------


@mcp.tool
async def search_openapi(query: str, top_k: int = 5) -> str:
    """Busca endpoints de API en lenguaje natural.

    Ejecuta el flujo híbrido HyDE + embedding denso + BM25 con fusión RRF
    y devuelve hasta ``top_k`` resultados en markdown compacto más contenido
    estructurado.  No incluye el JSON OpenAPI completo.

    Args:
        query: Consulta en lenguaje natural.
        top_k: Número de resultados a devolver. Rango: 1–10. Por defecto 5.

    Returns:
        Markdown compacto con los resultados encontrados.

    Raises:
        ToolError: Si ``top_k`` está fuera del rango [1, 10].
    """
    if not (1 <= top_k <= 10):
        raise ToolError(f"top_k debe estar entre 1 y 10 (recibido: {top_k})")

    try:
        scored_points = await domain_retrieval.search(
            query, top_k, _qdrant_client, _settings
        )
    except ValueError as exc:
        raise ToolError(str(exc)) from exc

    results: list[SearchResult] = []
    for ranking, point in enumerate(scored_points, start=1):
        composed = domain_result.compose_result(point, ranking)
        if composed is not None:
            results.append(composed)

    if not results:
        return "_No se encontraron resultados para la consulta._"

    # --- Formato markdown compacto ---
    lines: list[str] = ["## Resultados de búsqueda\n"]
    for r in results:
        lines.append(
            f"**{r.ranking}.** `{r.method} {r.path}` — {r.summary or ''}\n"
            f"   Categoría: {r.category or '—'} · "
            f"URL: `{r.call_url}` · "
            f"spec_ref: `{r.spec_ref}`\n"
        )

    lines.append("\n---\n")
    lines.append(
        "```json\n"
        + json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2)
        + "\n```"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Herramienta: get_endpoint_spec (AC-004 / AC-005 / BR-02 / API-02)
# ---------------------------------------------------------------------------

_SPEC_REF_SEGMENTS = 3


def _validate_spec_ref(spec_ref: str) -> None:
    """Valida que spec_ref tenga exactamente 3 segmentos no vacíos (source|METHOD|/path).

    Args:
        spec_ref: Referencia de la operación a validar.

    Raises:
        ToolError: Si el formato es inválido (BR-02 / AC-005).
    """
    if not spec_ref:
        raise ToolError(
            "spec_ref no puede estar vacío. "
            "Formato esperado: 'source_file|METHOD|/path'"
        )
    parts = spec_ref.split("|")
    if len(parts) != _SPEC_REF_SEGMENTS or any(not p for p in parts):
        raise ToolError(
            f"spec_ref inválido: {spec_ref!r}. "
            "Debe tener exactamente 3 segmentos no vacíos separados por '|': "
            "'source_file|METHOD|/path'"
        )


@mcp.tool
async def get_endpoint_spec(spec_ref: str) -> str:
    """Recupera el fragmento OpenAPI completo de un endpoint por su spec_ref.

    Devuelve markdown más contenido estructurado con el fragmento OpenAPI
    (MD-02), la URL de llamada y el deeplink.  Un ``spec_ref`` inválido o
    no encontrado se trata como error de herramienta (BR-02 / AC-005).

    Args:
        spec_ref: Referencia del endpoint en formato ``source_file|METHOD|/path``.

    Returns:
        Markdown con el fragmento OpenAPI, call_url y deeplink.

    Raises:
        ToolError: Si spec_ref tiene formato inválido o el endpoint no se encuentra.
    """
    _validate_spec_ref(spec_ref)

    found: list[SearchResult] = await domain_result.get_by_spec_ref(
        spec_ref,
        _qdrant_client,
        _settings.COLLECTION_NAME,
    )

    if not found:
        raise ToolError(
            f"Endpoint no encontrado: {spec_ref!r}. "
            "Verifica que el spec_ref sea correcto y que la colección esté indexada."
        )

    result = found[0]
    # Fragmento OpenAPI a partir de MD-03 (params/body ya normalizados en compose_result).
    openapi_fragment: dict[str, Any] = {
        "method": result.method,
        "path": result.path,
        "summary": result.summary,
        "description": result.description,
        "parameters": result.params,
        "requestBody": result.body,
    }

    lines: list[str] = [
        f"## Spec: `{spec_ref}`\n",
        f"**URL de llamada:** `{result.call_url}`",
        f"**Deeplink:** {result.deeplink or '—'}\n",
        "### Fragmento OpenAPI\n",
        "```json\n"
        + json.dumps(openapi_fragment, ensure_ascii=False, indent=2)
        + "\n```",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Prompt: find_backend_api (AC-006)
# ---------------------------------------------------------------------------


@mcp.prompt
def find_backend_api(need: str) -> str:
    """Guía al IDE por el flujo de búsqueda de API: buscar → presentar → pedir spec.

    Instruye al modelo a invocar ``search_openapi`` con la necesidad del usuario,
    presentar los resultados de forma legible y preguntar si desea el spec completo
    antes de invocar ``get_endpoint_spec``.

    Args:
        need: Descripción de la necesidad del usuario (lenguaje natural).

    Returns:
        Mensaje de usuario que instruye el flujo de búsqueda de API.
    """
    return (
        f"Necesito encontrar un endpoint de API para: {need}\n\n"
        "Por favor:\n"
        "1. Invoca `search_openapi(query=<need>)` con la necesidad anterior.\n"
        "2. Presenta los resultados al usuario con: ranking, método HTTP, path y summary.\n"
        "   Ejemplo: '1. POST /users — Crea un nuevo usuario'\n"
        "3. Pregunta al usuario si desea ver el spec completo de algún resultado "
        "**antes** de invocar `get_endpoint_spec`.\n"
        "   Solo invoca `get_endpoint_spec(spec_ref=<ref>)` si el usuario lo pide "
        "explícitamente.\n\n"
        "---\n"
        f"I need to find an API endpoint for: {need}\n\n"
        "Please:\n"
        "1. Call `search_openapi(query=<need>)` with the need above.\n"
        "2. Present results to the user with: ranking, HTTP method, path and summary.\n"
        "   Example: '1. POST /users — Create a new user'\n"
        "3. Ask the user if they want to see the full spec of any result "
        "**before** calling `get_endpoint_spec`.\n"
        "   Only call `get_endpoint_spec(spec_ref=<ref>)` if the user explicitly asks."
    )


# ---------------------------------------------------------------------------
# Middleware ASGI — rechaza peticiones GET en la ruta MCP (AC-002 / BR-01)
# ---------------------------------------------------------------------------


def _method_not_allowed_middleware(inner: ASGIApp) -> ASGIApp:
    """Devuelve un middleware ASGI que intercepta GET en la ruta MCP con 405.

    Args:
        inner: La aplicación ASGI subyacente a envolver.

    Returns:
        Nueva aplicación ASGI con el middleware aplicado.
    """
    mcp_path: str = _settings.MCP_PATH

    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http" and scope.get("method") == "GET":
            raw_path: str = str(scope.get("path", ""))
            normalized = raw_path.rstrip("/") or "/"
            if normalized == mcp_path.rstrip("/") or normalized == mcp_path:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 405,
                        "headers": [
                            [b"allow", b"POST, DELETE"],
                            [b"content-length", b"0"],
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": b""})
                return
        await inner(scope, receive, send)

    return middleware


# ---------------------------------------------------------------------------
# Aplicación ASGI de producción — referenciada por uvicorn como :app
# ---------------------------------------------------------------------------

_inner_app: StarletteWithLifespan = mcp.http_app(
    path=_settings.MCP_PATH,
    transport="streamable-http",
    stateless_http=True,
)

#: Referencia ASGI de producción.  Uvicorn la carga con ``smart_api_search.server:app``.
app: ASGIApp = _method_not_allowed_middleware(_inner_app)
