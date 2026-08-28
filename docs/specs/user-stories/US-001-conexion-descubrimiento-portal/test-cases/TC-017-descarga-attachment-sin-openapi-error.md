# TC-017 — Dado que una API no tiene attachment OpenAPI en el portal, Cuando el sistema intenta descargarlo, Entonces emite un mensaje de error claro y sin traza técnica

**Perspectiva:** Error
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-008 (Integraciones) — Descarga de attachment OpenAPI (JSON/YAML, tolerando BOM)
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El mock del portal devuelve el detalle de una API sin attachment OpenAPI (lista `attachments` vacía o ausente).
- El sistema tiene configurado el portal con `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| id_api | api-sin-attachment [propuesto] | API cuyos detalles no incluyen attachment OpenAPI |
| respuesta_detalle | `{"id": "api-sin-attachment", "attachments": []}` | Detalle sin attachment |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Obtener el detalle de `api-sin-attachment` desde el portal | El detalle indica que no hay attachment OpenAPI |
| 2 | Sistema | Intentar descargar el attachment OpenAPI | No hay URL de attachment; el sistema detecta la ausencia |
| 3 | Sistema | Emitir el mensaje de error | El mensaje indica claramente que la API no tiene attachment OpenAPI |
| 4 | Verificador (test) | Verificar el mensaje de error emitido | El mensaje es legible, no contiene stack trace ni detalles internos |

## Resultado esperado final

El sistema emite un mensaje de error claro del tipo «La API `api-sin-attachment` no tiene attachment OpenAPI» y continúa procesando el resto de APIs (no aborta el descubrimiento global). No se imprime ningún stack trace.

## Observaciones

- Relacionado con AC-009: el formato del mensaje debe cumplir los criterios de ese AC.
- Relacionado con AC-005: el fallo de esta API no debe detener la descarga del resto.
- El sistema NO debe intentar reconstruir el spec desde `resources[]` como fallback.
