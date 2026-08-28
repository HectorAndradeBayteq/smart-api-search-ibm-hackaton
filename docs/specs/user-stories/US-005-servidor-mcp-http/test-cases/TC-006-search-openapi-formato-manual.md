# TC-006 — Dado search_openapi con resultados, Cuando se inspecciona la respuesta, Entonces es markdown compacto más JSON estructurado sin OpenAPI completo del catálogo

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-003 — search_openapi DEBE devolver markdown compacto más contenido estructurado; NO el JSON OpenAPI completo
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Implementación de `search_openapi` en `server.py` revisable.
- Retrieval real pendiente de US-004 (stubs); validación por inspección del formato de salida.

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Leer el cuerpo de `search_openapi` | Construye markdown + bloque `json` de resultados compuestos |
| 2 | Revisor | Confirmar que no se serializa un documento OpenAPI completo del catálogo | Solo campos de SearchResult / lista de resultados |

## Resultado esperado final

Formato de salida conforme a AC-003 por revisión de código; prueba automatizada diferida (alcance + dependencia US-004).
