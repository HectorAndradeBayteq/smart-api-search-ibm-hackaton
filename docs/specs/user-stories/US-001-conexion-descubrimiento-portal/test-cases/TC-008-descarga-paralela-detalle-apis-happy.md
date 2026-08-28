# TC-008 — Dado que el portal tiene 25 APIs disponibles, Cuando el sistema descarga sus detalles, Entonces los descarga en paralelo con máximo 12 peticiones simultáneas y conserva el orden

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-005 (Integraciones) — Descarga en paralelo con límite de concurrencia
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas con portal activo: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El mock del portal devuelve 25 APIs en el listado (IDs del 1 al 25).
- El mock responde a `GET /apis/{id}` con el detalle de cada API sin errores.
- El entorno de prueba permite interceptar y contar peticiones concurrentes en vuelo.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| total_apis | 25 | Número de APIs cuyos detalles descargar |
| max_concurrencia | 12 | Límite máximo de peticiones en vuelo simultáneo |
| ids_apis | [1, 2, 3, ..., 25] [propuesto] | IDs de las APIs del listado |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Obtener el listado de 25 APIs mediante paginación | Se obtiene la lista completa de 25 IDs |
| 2 | Sistema | Iniciar la descarga de detalles `GET /apis/{id}` con semáforo de concurrencia máxima 12 | En ningún instante hay más de 12 peticiones en vuelo simultáneo |
| 3 | Verificador (test) | Registrar el número máximo de peticiones activas en paralelo durante la descarga | El pico de concurrencia es ≤ 12 |
| 4 | Sistema | Completar la descarga de todos los detalles | Se obtienen 25 detalles sin errores |
| 5 | Verificador (test) | Verificar el orden de los resultados obtenidos | Los detalles están ordenados en el mismo orden que el listado original (ID 1 primero, ID 25 último) |

## Resultado esperado final

El sistema descarga los 25 detalles en paralelo con un máximo de 12 peticiones en vuelo simultáneo. El orden de los resultados coincide con el orden del listado original. No se produce ningún error durante la descarga.

## Observaciones

- El semáforo de concurrencia puede implementarse con `asyncio.Semaphore(12)` u equivalente.
- Para verificar la concurrencia en prueba, se puede usar un contador atómico de peticiones activas en el mock.
