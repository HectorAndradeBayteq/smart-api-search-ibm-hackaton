---
name: Estándares de API
domain: api
status: Active
last_update: 2025-07-14
source_adrs: [ADR-001, ADR-013]
tags: [fastmcp, mcp, uvicorn, asgi, streamable-http]
---

# Estándares de API

Este estándar cubre las normas del dominio de interfaces y APIs del proyecto `smart-api-search`. Aplica al servidor MCP, su framework, transporte, y convenciones de entrypoint ASGI. Define qué herramientas y configuraciones son obligatorias y cómo debe estructurarse el arranque del servidor para garantizar su correcto funcionamiento con los clientes MCP.

## Servidor MCP: framework y transporte

**ID:** servidor-mcp-framework
**Estado:** Active

El servidor MCP **DEBE** implementarse usando **FastMCP** con transporte `streamable-http`. El servidor **DEBE** servirse con **uvicorn** como ASGI server. El uso de `stdio` como transporte está prohibido para despliegues accesibles por red. El uso de `sse` (Server-Sent Events) está deprecado y no **DEBE** usarse en nuevas implementaciones.

### Excepciones

Ninguna. El transporte `stdio` solo es aceptable en pruebas unitarias que no requieran un cliente HTTP real.

## Entrypoint ASGI del servidor MCP

**ID:** entrypoint-asgi
**Estado:** Active

El servidor **DEBE** arrancarse mediante la referencia ASGI directa del módulo (`uvicorn smart_api_search.server:app`). El paquete raíz (`smart_api_search/__init__.py`) **NO DEBE** reexportar la app ASGI ni ningún símbolo que sombree a sus propios submódulos. El módulo **NO DEBE** usarse como `__main__` para arrancar el servidor de producción.

Este requisito previene el error de doble carga de módulo verificado en producción (Anexo A-6 de la arquitectura): cuando uvicorn importa la app ASGI y el módulo ya fue cargado vía `__main__`, se instancia una segunda copia del servidor sin las herramientas MCP registradas, produciendo el síntoma "Connected / No tools available".

Las **pruebas de integración DEBEN** importar la app desde `smart_api_search.server:app`, el mismo camino que usa producción.

### Excepciones

Ninguna.

## Criterios de cumplimiento

| ID | Requisito | Descripción | Origen | Automatizable | Enfoque | Verificación |
|----|-----------|-------------|--------|---------------|---------|--------------|
| CR-001 | servidor-mcp-framework | El servidor **DEBE** usar FastMCP con transporte `streamable-http` | [ADR-001](../adr/ADR-001-fastmcp-servidor-mcp.md) | yes | bloqueante | no |
| CR-002 | servidor-mcp-framework | El servidor **DEBE** servirse con uvicorn como ASGI server | [ADR-001](../adr/ADR-001-fastmcp-servidor-mcp.md) | yes | bloqueante | no |
| CR-003 | entrypoint-asgi | El entrypoint de producción **DEBE** ser `smart_api_search.server:app` | [ADR-013](../adr/ADR-013-arranque-servidor-mcp-asgi.md) | yes | bloqueante | no |
| CR-004 | entrypoint-asgi | `smart_api_search/__init__.py` **NO DEBE** reexportar la app ASGI | [ADR-013](../adr/ADR-013-arranque-servidor-mcp-asgi.md) | yes | bloqueante | no |

## Referencias

- [ADR-001: FastMCP como framework del servidor MCP](../adr/ADR-001-fastmcp-servidor-mcp.md)
- [ADR-013: Arranque del servidor MCP por referencia ASGI](../adr/ADR-013-arranque-servidor-mcp-asgi.md)
- [Especificación MCP — transporte streamable-http](https://spec.modelcontextprotocol.io/specification/basic/transports/)
