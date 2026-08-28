---
id: ADR-013
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [uvicorn, asgi, entrypoint, module-loading, api]
supersedes: null
superseded_by: null
emits: [api/CR-003, api/CR-004]
---

# ADR-013: Arranque del servidor MCP por referencia ASGI

> ⚠ **Lección aprendida de fallo en producción (Anexo A-6):** arrancar con `__main__` y reexportar la app en `__init__.py` provoca que el módulo se cargue dos veces; uvicorn sirve una segunda instancia sin herramientas registradas. El cliente muestra "Connected" pero "No tools available".

## Contexto

Al arrancar el servidor MCP con `python -m smart_api_search` (ejecución de `__main__`), Python importa el módulo `smart_api_search.__main__`, que a su vez importa `smart_api_search.server`. Si además `smart_api_search/__init__.py` reexporta la app (p. ej. `from smart_api_search.server import app`), uvicorn carga el módulo por segunda vez mediante la referencia ASGI, obteniendo una instancia nueva sin las herramientas registradas. El cliente MCP establece la conexión pero no encuentra ninguna herramienta.

## Decisión

El servidor se expone mediante la **referencia ASGI del módulo** (`uvicorn smart_api_search.server:app`), nunca ejecutando el módulo como `__main__`. El paquete (`smart_api_search/__init__.py`) **no debe reexportar símbolos que sombreen a sus propios submódulos**, en particular la app ASGI.

## Alternativas consideradas

- **Arranque con `python -m smart_api_search`**: error verificado en producción; descartado.
- **Reexportar la app en `__init__.py`**: provoca doble carga del módulo con uvicorn; descartado.

## Consecuencias

### Positivas

- Uvicorn carga la app desde la referencia ASGI directa; las herramientas MCP están registradas correctamente.
- Las pruebas de integración pueden importar la app desde `smart_api_search.server:app` de forma consistente con producción.
- Elimina la clase de errores de doble carga de módulo verificada en producción.

### Negativas / trade-offs

- El comando de arranque debe ser siempre `uvicorn smart_api_search.server:app`; no se puede usar `python -m smart_api_search` como alternativa.
- `__init__.py` del paquete debe mantenerse limpio de reexportaciones de la app; esto debe vigilarse en revisiones de código.

## Referencias

- [ADR-001: FastMCP como framework del servidor MCP](ADR-001-fastmcp-servidor-mcp.md)
- [Estándar API](../standards/api.md)
