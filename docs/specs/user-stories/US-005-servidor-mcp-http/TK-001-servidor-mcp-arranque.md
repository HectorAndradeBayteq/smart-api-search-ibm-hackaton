# TK-001: Configuración del servidor MCP HTTP y middleware de método

**Estado:** Ready
**Historia:** [US-005](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Crear el módulo `smart_api_search/server.py` que instancia el servidor FastMCP con transporte `streamable-http`, lo expone como referencia ASGI (`smart_api_search.server:app`) arrancado con uvicorn, y lee los parámetros de red desde `Settings`: `MCP_HOST` (defecto `127.0.0.1`), `MCP_PORT` (defecto `8000`) y `MCP_PATH` (defecto `/mcp`). Añadir un middleware ASGI ligero que intercepte peticiones `GET` al endpoint MCP y responda `405 Method Not Allowed` con cabecera `Allow: POST, DELETE`. El paquete `smart_api_search/__init__.py` NO debe reexportar la app ni ningún símbolo del módulo `server` (BR-01 / ADR-013).

## Dependencias

- `fastmcp` ≥ 2.0 — instanciación del servidor MCP y transporte `streamable-http`
- `uvicorn` ≥ 0.30 — servidor ASGI; el script `.ps1` y la documentación deben usar siempre `uvicorn smart_api_search.server:app`
- `python-dotenv` — lectura de variables de entorno desde `.env` vía `Settings`
- `smart_api_search.config.Settings` — provee `MCP_HOST`, `MCP_PORT`, `MCP_PATH` (MD-05)

## Referencias

- **Arquitectura:** [ADR-001 — FastMCP como framework del servidor MCP](../../adr/ADR-001-fastmcp-servidor-mcp.md)
- **Arquitectura:** [ADR-013 — Arranque del servidor MCP por referencia ASGI](../../adr/ADR-013-arranque-servidor-mcp-asgi.md)
- **Documentación técnica:** [MD-05: Settings](../../specs/technical-docs/smart-api-search.md#md-05)
- **Documentación técnica:** [API-01: search_openapi](../../specs/technical-docs/smart-api-search.md#api-01)
- **Documentación técnica:** [API-02: get_endpoint_spec](../../specs/technical-docs/smart-api-search.md#api-02)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    ├── + server.py          # Instancia FastMCP, registra middleware GET→405, expone app ASGI
    └── ~ __init__.py        # Verificar que NO reexporta símbolos de server.py (mantener limpio)
```

## Plan de implementación

- [x] **IT-01** — Crear `src/smart_api_search/server.py` con la instancia FastMCP
  Instanciar `mcp = FastMCP(name="smart-api-search", ...)` con `stateless_http=True`. Leer `Settings` para obtener `MCP_HOST`, `MCP_PORT` y `MCP_PATH`. Exponer `app = mcp.streamable_http_app()` (u equivalente FastMCP ≥ 2.0) como variable de módulo de nivel superior — esta es la referencia ASGI de producción.
- [x] **IT-02** — Implementar el middleware ASGI para rechazar peticiones GET
  Envolver `app` con un middleware ASGI puro (función o clase compatible con la interfaz ASGI 3) que inspeccione `scope["type"] == "http"` y `scope["method"] == "GET"` sobre la ruta MCP (`MCP_PATH`). Si coincide, responder `405 Method Not Allowed` con cabecera `Allow: POST, DELETE` sin llamar al siguiente handler. En cualquier otro caso, pasar el control a la app subyacente.
- [x] **IT-03** — Verificar que `__init__.py` no reexporta símbolos de `server.py`
  Leer `src/smart_api_search/__init__.py` y confirmar que no contiene ninguna importación de `server` ni de `app`. Si contiene alguna, eliminarla. El archivo debe quedar con el docstring de módulo solamente (estado ya verificado en el repositorio).
- [x] **IT-04** — Añadir tipos completos y anotaciones mypy
  Asegurar que `server.py` pasa `mypy --strict` sin errores nuevos. Anotar la función/clase del middleware con los tipos ASGI estándar (`Scope`, `Receive`, `Send` de `typing` o `asgiref`).
