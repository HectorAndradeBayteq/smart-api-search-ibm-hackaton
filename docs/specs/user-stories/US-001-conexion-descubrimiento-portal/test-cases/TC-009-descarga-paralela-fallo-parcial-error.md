# TC-009 — Dado que algunas llamadas a GET /apis/{id} fallan, Cuando el sistema descarga los detalles en paralelo, Entonces los fallos parciales no abortan el descubrimiento del resto

**Perspectiva:** Error
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-005 (Integraciones) — Descarga en paralelo con límite de concurrencia
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas con portal activo: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El mock del portal devuelve 5 APIs en el listado (IDs 1 al 5).
- El mock responde con `500 Internal Server Error` para `GET /apis/3` y con `200 OK` para el resto.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| total_apis | 5 | Número de APIs en el listado |
| ids_exitosos | [1, 2, 4, 5] [propuesto] | APIs que responden con éxito |
| ids_fallidos | [3] [propuesto] | APIs que responden con error 500 |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Obtener el listado de 5 APIs | Lista con IDs 1 al 5 |
| 2 | Sistema | Iniciar descarga en paralelo de `GET /apis/1` al `GET /apis/5` | Se lanzan las 5 peticiones concurrentes |
| 3 | Mock | Responder `500 Internal Server Error` a `GET /apis/3` | La petición de la API 3 falla |
| 4 | Sistema | Procesar el fallo de `GET /apis/3` | El error es capturado; no se lanza excepción global que detenga el proceso |
| 5 | Sistema | Completar la descarga de las APIs 1, 2, 4 y 5 con éxito | Se obtienen 4 detalles válidos |
| 6 | Verificador (test) | Verificar el resultado final | El proceso devuelve 4 detalles válidos y registra el fallo de la API 3 sin abortar |

## Resultado esperado final

El sistema devuelve los detalles de las 4 APIs que respondieron correctamente. El fallo de la API 3 se registra (log o resultado marcado como error) pero no interrumpe la descarga ni el proceso de descubrimiento del resto. No se lanza excepción no capturada.

## Observaciones

- Verificar que el fallo parcial se comunica de alguna forma (log, resultado con indicador de error) para no perder visibilidad.
- Relacionado con AC-009 en cuanto a la forma en que se comunica el fallo de una API sin attachment o con error de descarga.
