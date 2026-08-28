# TC-010 — Dado que el portal tiene exactamente 12 APIs, Cuando el sistema descarga sus detalles en paralelo, Entonces lanza exactamente 12 peticiones simultáneas (límite exacto)

**Perspectiva:** Límite
**Tipo de prueba:** Unit
**Prioridad:** Media
**Criterio de aceptación:** AC-005 (Integraciones) — Descarga en paralelo con límite de concurrencia
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas con portal activo: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El mock del portal devuelve exactamente 12 APIs en el listado.
- El mock responde con `200 OK` a todas las peticiones de detalle.
- El entorno permite medir el número de peticiones activas simultáneamente.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| total_apis | 12 | Número exacto igual al límite de concurrencia |
| max_concurrencia | 12 | Límite máximo configurado |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Obtener el listado de 12 APIs | Lista con 12 IDs |
| 2 | Sistema | Iniciar descarga en paralelo con semáforo de 12 | Se lanzan hasta 12 peticiones simultáneas |
| 3 | Verificador (test) | Medir el pico de concurrencia | El pico es exactamente 12 (no más, no menos si hay 12 disponibles) |
| 4 | Sistema | Completar la descarga | Se obtienen 12 detalles sin errores |

## Resultado esperado final

Con exactamente 12 APIs, el sistema las descarga todas en una única ronda de concurrencia máxima (12 peticiones simultáneas). El semáforo se respeta: nunca más de 12 en vuelo. Los 12 detalles se obtienen correctamente.

## Observaciones

- Este caso prueba el límite exacto del semáforo de concurrencia (12 = max_concurrencia).
- Complementario al TC-008 (25 > 12) y al caso implícito de 1 API (1 < 12).
