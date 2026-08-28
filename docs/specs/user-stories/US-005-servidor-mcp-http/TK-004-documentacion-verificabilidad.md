# TK-004: Documentación de configuración de clientes y verificabilidad ASGI

**Estado:** Ready
**Historia:** [US-005](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Entregar tres artefactos documentales y una verificación de integración:

1. **Ejemplo de configuración de cliente MCP** (`type: http` con la URL completa) para IBM Bob, VS Code, Cursor y GitHub Copilot, usable sin modificación una vez el servidor está en marcha.
2. **Script `start-server.ps1`** en la raíz del repositorio que arranca el servidor usando el Python del entorno virtual (`.venv/Scripts/python.exe`) y la referencia ASGI `smart_api_search.server:app`.
3. **Actualización del README del repositorio** con una sección dedicada que explique cómo registrar el servidor en IBM Bob (y los demás IDEs soportados).
4. **Verificación ASGI de producción**: un test que importe `app` desde `smart_api_search.server` (el mismo camino que usa uvicorn en producción) y afirme que expone exactamente las dos herramientas (`search_openapi`, `get_endpoint_spec`) y el prompt (`find_backend_api`). Importar la aplicación por cualquier otro camino (p.ej. instancia local en test) no satisface AC-009.

## Dependencias

- `smart_api_search.server.app` (TK-001) — objeto ASGI de producción sobre el que opera la verificación
- Herramientas registradas (TK-002) y prompt registrado (TK-003) — la verificación afirma su presencia en `app`
- `fastmcp` ≥ 2.0 — API de introspección del servidor (p.ej. `mcp.list_tools()`, `mcp.list_prompts()` o equivalente) para leer las herramientas y prompts registrados
- `pytest` ≥ 8.2 — framework de pruebas para la verificación ASGI

## Referencias

- **Arquitectura:** [ADR-001 — FastMCP como framework del servidor MCP](../../adr/ADR-001-fastmcp-servidor-mcp.md)
- **Arquitectura:** [ADR-013 — Arranque del servidor MCP por referencia ASGI](../../adr/ADR-013-arranque-servidor-mcp-asgi.md)
- **Arquitectura:** [ADR-004 — Compuerta de calidad: pytest, mypy, ruff](../../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md)
- **Documentación técnica:** [MD-05: Settings — campos MCP_HOST, MCP_PORT, MCP_PATH](../../specs/technical-docs/smart-api-search.md#md-05)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
├── + start-server.ps1                  # Script PS1 de arranque con el Python del venv
├── ~ README.md                         # Añadir sección "Registrar el servidor en IBM Bob"
├── ~ .bob/config.json (o equivalente)  # Añadir ejemplo de configuración de cliente MCP tipo http
└── tests/
    └── + test_server_asgi.py           # Verificación ASGI: importa app desde smart_api_search.server y afirma herramientas + prompt
```

## Plan de implementación

- [ ] **IT-01** — Crear `start-server.ps1` en la raíz del repositorio
  El script debe: (1) activar el entorno virtual si no está activo (`.venv/Scripts/Activate.ps1`); (2) lanzar uvicorn con `& ".venv/Scripts/python.exe" -m uvicorn smart_api_search.server:app --host $MCP_HOST_OR_DEFAULT --port $MCP_PORT_OR_DEFAULT`. Los valores de host y puerto se leen de variables de entorno con fallback a `127.0.0.1` y `8000` respectivamente.
- [ ] **IT-02** — Crear el ejemplo de configuración de cliente MCP
  Generar un bloque de configuración `type: http` + URL (`http://127.0.0.1:8000/mcp`) para cada IDE soportado. Formato por IDE: IBM Bob (`mcp.json` o equivalente), VS Code (`settings.json` → `mcp.servers`), Cursor (`.cursor/mcp.json`), GitHub Copilot (`.github/copilot-mcp.json`). El ejemplo debe ser copiable sin modificación para un servidor local con los valores por defecto.
- [ ] **IT-03** — Actualizar el README del repositorio
  Añadir una sección `## Servidor MCP` (o `## Registrar en el IDE`) que explique: (1) cómo arrancar con `start-server.ps1`, (2) cómo registrar el servidor en IBM Bob con el bloque de configuración del paso IT-02, (3) referencia a los demás IDEs soportados.
- [ ] **IT-04** — Crear `tests/test_server_asgi.py` con la verificación ASGI de producción
  Importar `from smart_api_search.server import app` (el mismo camino que uvicorn en producción; no crear una instancia local). Usar la API de introspección de FastMCP sobre `app` (p.ej. `app.list_tools()` / `app.list_prompts()` o la interfaz equivalente de FastMCP ≥ 2.0) para obtener los nombres registrados. Afirmar: herramientas contienen `search_openapi` y `get_endpoint_spec`; prompts contienen `find_backend_api`. El test debe pasar sin credenciales reales (no arranca el servidor, solo verifica el objeto en memoria).
- [ ] **IT-05** — Verificar que el test pasa con `pytest` y `mypy --strict`
  Ejecutar `pytest tests/test_server_asgi.py -v` y confirmar que el test verde. Asegurar anotaciones de tipos en `test_server_asgi.py` sin errores mypy nuevos.
