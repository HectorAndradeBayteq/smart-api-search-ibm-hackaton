# TK-003: Prompt find_backend_api e instrucciones del servidor

**Estado:** Ready
**Historia:** [US-005](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Registrar en el servidor FastMCP el prompt `find_backend_api(need: str)` y configurar las instrucciones del servidor (`server_instructions`). El prompt guía al IDE por el flujo: **buscar** (invocar `search_openapi`) → **presentar** los resultados al usuario → **pedir el spec** solo si el usuario lo solicita explícitamente (invocar `get_endpoint_spec`). Las instrucciones del servidor deben contener las cuatro directivas de AC-007: (1) usar esta base de conocimiento para descubrir APIs, (2) no buscar en el workspace del usuario, (3) no traducir los nombres de categoría y (4) no pegar JSON salvo petición explícita del usuario.

## Dependencias

- `smart_api_search.server` (TK-001) — instancia `mcp` en la que se registra el prompt con `@mcp.prompt` y se configuran las instrucciones
- Herramienta `search_openapi` (TK-002) — el prompt la invoca en el primer paso del flujo
- Herramienta `get_endpoint_spec` (TK-002) — el prompt la invoca solo si el usuario pide el spec
- `fastmcp` ≥ 2.0 — decorador `@mcp.prompt` y campo `instructions` del servidor MCP

## Referencias

- **Arquitectura:** [ADR-001 — FastMCP como framework del servidor MCP](../../adr/ADR-001-fastmcp-servidor-mcp.md)
- **Documentación técnica:** [API-01: search_openapi](../../specs/technical-docs/smart-api-search.md#api-01)
- **Documentación técnica:** [API-02: get_endpoint_spec](../../specs/technical-docs/smart-api-search.md#api-02)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ server.py    # Registrar @mcp.prompt find_backend_api y configurar server_instructions
```

## Plan de implementación

- [ ] **IT-01** — Implementar `find_backend_api` como prompt MCP en `server.py`
  Decorar con `@mcp.prompt`. Firma: `def find_backend_api(need: str) -> list[Message]` (o el tipo de retorno equivalente que espera FastMCP ≥ 2.0). El prompt devuelve un mensaje de usuario que instruye al modelo a: (1) invocar `search_openapi(query=need)`, (2) presentar los resultados en formato legible al usuario indicando ranking, método, path y summary, (3) preguntar si desea ver el spec completo de algún resultado antes de invocar `get_endpoint_spec`. El texto del prompt debe estar en español e inglés o en el idioma que el usuario indique.
- [ ] **IT-02** — Configurar las instrucciones del servidor en la instancia FastMCP
  Pasar el campo `instructions` (o equivalente FastMCP) al construir `mcp = FastMCP(...)` con las cuatro directivas de AC-007: (1) "Usa esta base de conocimiento para descubrir APIs del catálogo; no busques APIs en el workspace del usuario.", (2) "No busques en el workspace del usuario.", (3) "No traduzcas los nombres de categoría; preséntalos tal como aparecen en los resultados.", (4) "No pegues JSON del spec a menos que el usuario lo solicite explícitamente.".
- [ ] **IT-03** — Añadir tipos completos y anotaciones mypy
  Asegurar que el prompt y las instrucciones en `server.py` pasan `mypy --strict` sin errores nuevos.
