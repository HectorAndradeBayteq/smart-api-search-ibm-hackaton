# TC-004 — Dado un spec_ref con formato inválido, Cuando se invoca get_endpoint_spec, Entonces devuelve tool_error sin propagar excepción del servidor

**Perspectiva:** Error
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-005 — Un spec_ref inválido o no encontrado en get_endpoint_spec DEBE marcarse como error de herramienta; NO DEBE propagarse como excepción del servidor
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2025-08-28

## Precondiciones

- `smart_api_search.server` importable con `mcp` accesible.
- La herramienta `get_endpoint_spec` registrada en `mcp`.
- Sin conexión real a Qdrant — la validación del formato ocurre antes de cualquier llamada externa.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| spec_ref inválido (2 segmentos) | `"portal:user-api\|POST"` | Falta el tercer segmento `/path` |
| spec_ref inválido (segmento vacío) | `"portal:user-api\|\|/users"` | Segmento vacío no permitido |
| spec_ref inválido (vacío) | `""` | Cadena vacía |
| excepción esperada | `fastmcp.exceptions.ToolError` | Debe lanzarse, no excepción genérica del servidor |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Test | `from smart_api_search.server import mcp` | Sin error |
| 2 | Test | `await mcp.call_tool("get_endpoint_spec", {"spec_ref": "portal:user-api|POST"})` | Lanza `ToolError` |
| 3 | Test | Verificar que el tipo de excepción es `ToolError` (o `McpError`), no `ValueError` ni `Exception` genérica | `True` |
| 4 | Test | Verificar que el mensaje de error es descriptivo (contiene referencia al formato esperado) | `True` |

## Resultado esperado final

`mcp.call_tool("get_endpoint_spec", ...)` con `spec_ref` inválido lanza `ToolError` (BR-02). La herramienta no propaga `ValueError`, `KeyError` ni ninguna excepción que el servidor convertiría en error 500. El servidor sigue operativo.

## Observaciones

BR-02 establece que `get_endpoint_spec` DEBE tratar un `spec_ref` inválido como error de herramienta. La validación del formato (3 segmentos no vacíos) es local y no requiere Qdrant. Cubre el escenario de formato incorrecto; el escenario "no encontrado en colección" requiere Qdrant mockeado y queda para pruebas de integración.
