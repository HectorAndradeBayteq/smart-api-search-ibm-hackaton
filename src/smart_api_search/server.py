"""Servidor MCP HTTP para Smart API Search.

Expone las herramientas de búsqueda semántica y consulta de spec como herramientas
MCP sobre transporte ``streamable-http``.

Arranque::

    uvicorn smart_api_search.server:app --host 127.0.0.1 --port 8000

No ejecutar como ``__main__``; ver ADR-013.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.http import StarletteWithLifespan

from smart_api_search.config import Settings

_settings = Settings()

# ---------------------------------------------------------------------------
# Tipos ASGI estándar (PEP 3333 / ASGI 3)
# ---------------------------------------------------------------------------

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]

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
