---
id: ADR-001
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [fastmcp, mcp, uvicorn, streamable-http, api]
supersedes: null
superseded_by: null
emits: [api/CR-001, api/CR-002]
---

# ADR-001: FastMCP como framework del servidor MCP

## Contexto

El sistema debe exponer herramientas MCP a IDEs y clientes compatibles (IBM Bob, VS Code, Cursor, GitHub Copilot). La elección del framework MCP y del transporte determina la compatibilidad con el ecosistema de clientes modernos. El protocolo MCP admite varios transportes: `stdio`, `sse` y `streamable-http`; cada uno tiene implicaciones distintas en términos de compatibilidad, ciclo de vida del proceso y despliegue.

## Decisión

Usar **FastMCP** con transporte `streamable-http` servido con **uvicorn** como framework del servidor MCP. El servidor se expone como una aplicación ASGI, arrancada con `uvicorn smart_api_search.server:app`.

## Alternativas consideradas

- **`stdio`**: solo válido para uso local sin cliente HTTP; no sirve para IDEs que consumen el servidor por red.
- **`sse` (Server-Sent Events)**: marcado como deprecated en la especificación MCP en favor de `streamable-http`; no se considera para nuevas implementaciones.

## Consecuencias

### Positivas

- Compatibilidad nativa con todos los clientes MCP modernos (IBM Bob, VS Code MCP, Cursor, GitHub Copilot).
- El transporte `streamable-http` es el estándar actual de la especificación MCP; garantiza compatibilidad futura.
- FastMCP simplifica el registro de herramientas y el ciclo de vida del servidor.

### Negativas / trade-offs

- El servidor requiere uvicorn como ASGI server; el entrypoint debe ser una referencia ASGI, no `__main__`.
- Arrancar con `python -m smart_api_search` o con `__main__` puede provocar doble carga del módulo si el paquete reexporta la app (ver ADR-013).

## Referencias

- [ADR-013: Arranque del servidor MCP por referencia ASGI](ADR-013-arranque-servidor-mcp-asgi.md)
- [Estándar API](../standards/api.md)
- [Especificación MCP — transporte streamable-http](https://spec.modelcontextprotocol.io/specification/basic/transports/)
