# TC-010 — Dados los ejemplos de cliente MCP y start-server.ps1, Cuando se revisan en el repo, Entonces hay config usable (Bob/VS Code/Cursor/Copilot) y script con Python del venv

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-010 — Ejemplo de configuración MCP (type http/URL) para Bob, VS Code, Cursor y Copilot + script .ps1 con Python del venv
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Artefactos de documentación en la rama (no se automatiza por diseño).

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Abrir `.bob/mcp.json` y `.github/copilot-mcp.json` | URL MCP y tipo streamable-http/http |
| 2 | Revisor | Revisar tabla de IDEs en README | Menciona Bob, VS Code, Cursor, Copilot |
| 3 | Revisor | Revisar `start-server.ps1` | Usa Python del `.venv` y referencia ASGI |

## Resultado esperado final

Entregables de configuración y arranque verificados manualmente (AC no crítico).
