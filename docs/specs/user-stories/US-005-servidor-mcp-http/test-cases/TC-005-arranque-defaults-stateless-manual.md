# TC-005 — Dado Settings y el entrypoint ASGI, Cuando se revisan host/port/path y stateless_http, Entonces coinciden los defaults MCP y el modo sin estado

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-001 — El servidor DEBE arrancar con uvicorn en MCP_HOST, MCP_PORT y MCP_PATH (defaults 127.0.0.1, 8000, /mcp) en modo sin estado
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Código de `Settings` y `mcp.http_app(..., stateless_http=True)` disponible en la rama.
- Decisión de alcance: solo TCs automatizados para AC críticos; este criterio se valida por revisión manual.

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Verificar defaults en `config.py` | `MCP_HOST=127.0.0.1`, `MCP_PORT=8000`, `MCP_PATH=/mcp` |
| 2 | Revisor | Verificar `server.py` `http_app(..., stateless_http=True)` | Modo sin estado activo |
| 3 | Revisor | Verificar `start-server.ps1` usa referencia ASGI | Arranque por `smart_api_search.server:app` |

## Resultado esperado final

Defaults y modo sin estado confirmados por inspección; automatización diferida por alcance autorizado.
