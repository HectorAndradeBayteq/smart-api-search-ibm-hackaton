"""Pruebas de verificabilidad ASGI del servidor MCP.

Cubre:
- TC-001 / AC-008: __init__.py no reexporta símbolos de server.py
- TC-002 / AC-009: mcp de producción expone search_openapi, get_endpoint_spec y find_backend_api
- TC-003 / AC-002: middleware responde 405 a peticiones GET en la ruta MCP
- TC-004 / AC-005: spec_ref inválido lanza ToolError, no excepción del servidor
"""
from __future__ import annotations

import pytest
import pytest_asyncio  # noqa: F401  # Required for asyncio test discovery in strict mode

# ---------------------------------------------------------------------------
# TC-001 / AC-008 — __init__.py no reexporta símbolos de server.py
# ---------------------------------------------------------------------------


def test_init_no_reexports_app() -> None:
    """TC-001: smart_api_search.__init__ no debe exponer 'app' ni símbolos de server."""
    import smart_api_search

    assert not hasattr(smart_api_search, "app"), (
        "__init__.py no debe reexportar 'app' de server.py (ADR-013)"
    )
    assert not hasattr(smart_api_search, "mcp"), (
        "__init__.py no debe reexportar 'mcp' de server.py (ADR-013)"
    )
    assert not hasattr(smart_api_search, "server"), (
        "__init__.py no debe reexportar el módulo 'server' (ADR-013)"
    )


# ---------------------------------------------------------------------------
# TC-002 / AC-009 — mcp de producción expone herramientas y prompt
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_production_mcp_exposes_tools_and_prompt() -> None:
    """TC-002: mcp importado desde smart_api_search.server expone las 2 herramientas y el prompt."""
    from smart_api_search.server import mcp  # ruta de producción (misma que usa uvicorn)

    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert "search_openapi" in tool_names, "Herramienta 'search_openapi' no registrada"
    assert "get_endpoint_spec" in tool_names, "Herramienta 'get_endpoint_spec' no registrada"

    prompts = await mcp.list_prompts()
    prompt_names = {p.name for p in prompts}
    assert "find_backend_api" in prompt_names, "Prompt 'find_backend_api' no registrado"


# ---------------------------------------------------------------------------
# TC-003 / AC-002 — middleware responde 405 a GET en la ruta MCP
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_middleware_get_returns_405() -> None:
    """TC-003: una petición GET al endpoint MCP recibe 405 + Allow: POST, DELETE."""
    import httpx
    from httpx import ASGITransport

    from smart_api_search.server import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/mcp")

    assert response.status_code == 405, (
        f"Esperado 405, recibido {response.status_code}"
    )
    allow_header = response.headers.get("allow", "")
    assert "POST" in allow_header, f"Cabecera Allow no contiene POST: {allow_header!r}"
    assert "DELETE" in allow_header, f"Cabecera Allow no contiene DELETE: {allow_header!r}"


# ---------------------------------------------------------------------------
# TC-004 / AC-005 — spec_ref inválido lanza ToolError
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_endpoint_spec_invalid_spec_ref_raises_tool_error() -> None:
    """TC-004: spec_ref con formato inválido provoca ToolError, no excepción del servidor."""
    from fastmcp.exceptions import ToolError

    from smart_api_search.server import mcp

    invalid_refs = [
        "portal:user-api|POST",  # 2 segmentos, falta path
        "portal:user-api||/users",  # segmento vacío
        "",  # cadena vacía
    ]
    for spec_ref in invalid_refs:
        with pytest.raises(ToolError, match=r"(?i)(spec_ref|invalid|format)"):
            await mcp.call_tool("get_endpoint_spec", {"spec_ref": spec_ref})
