# TC-007 — Dado get_endpoint_spec con punto encontrado, Cuando se inspecciona la respuesta, Entonces incluye markdown, fragmento OpenAPI, call_url y deeplink

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-004 — get_endpoint_spec DEBE devolver markdown + fragmento OpenAPI + URL de llamada + deeplink
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Implementación de `get_endpoint_spec` en `server.py` revisable.
- `get_by_spec_ref` stub (US-004); happy path automatizado diferido.

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Leer el happy path de `get_endpoint_spec` | Emite `call_url`, `deeplink` y bloque JSON del fragmento |
| 2 | Revisor | Confirmar manejo de `raw_spec` | Parseo JSON o fallback `{"raw": ...}` |

## Resultado esperado final

Contrato de salida AC-004 verificado por inspección; automatización diferida por alcance autorizado.
