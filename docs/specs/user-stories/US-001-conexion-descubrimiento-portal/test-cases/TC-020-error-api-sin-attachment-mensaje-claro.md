# TC-020 — Dado que una API en el portal no tiene attachment OpenAPI, Cuando el sistema intenta descargarlo, Entonces emite mensaje de error claro sin traza técnica y continúa con el resto

**Perspectiva:** Error
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-009 (Casos de uso) — Mensajes de error claros sin traza técnica
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El mock del portal devuelve 3 APIs; la segunda (`api-2`) no tiene attachment OpenAPI.
- El sistema tiene configurado el portal activo con `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| id_api_sin_attachment | api-2 [propuesto] | API sin attachment en el detalle |
| ids_apis_con_attachment | [api-1, api-3] [propuesto] | APIs con attachment válido |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Descubrir las 3 APIs del portal | Listado con `api-1`, `api-2`, `api-3` |
| 2 | Sistema | Intentar descargar el attachment de `api-2` | La API no tiene attachment; se detecta la ausencia |
| 3 | Sistema | Emitir el mensaje de error para `api-2` | El mensaje indica que `api-2` no tiene attachment OpenAPI; sin stack trace |
| 4 | Sistema | Continuar con la descarga de `api-1` y `api-3` | Los attachments de las otras APIs se descargan correctamente |
| 5 | Verificador (test) | Verificar la salida del proceso | Mensaje de error legible para `api-2` y 2 specs descargados para `api-1` y `api-3` |

## Resultado esperado final

El sistema emite un mensaje de error claro para la API sin attachment (p. ej.: «La API api-2 no tiene attachment OpenAPI») sin stack trace, y continúa procesando las otras 2 APIs. El proceso finaliza con 2 specs válidos y 1 error notificado.

## Observaciones

- Este TC combina AC-009 (mensaje claro) y AC-005 (tolerancia a fallos parciales).
- Diferencia con TC-017: ese TC verifica el comportamiento desde la perspectiva de AC-008 (attachment); este TC verifica el formato del mensaje de error desde la perspectiva de AC-009.
