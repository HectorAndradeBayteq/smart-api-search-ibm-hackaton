# TC-006 — Dado que el portal devuelve múltiples páginas de APIs, Cuando el sistema lista las APIs, Entonces pagina con GET /apis?page=N hasta cubrir el total indicado por count

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-004 (Integraciones) — Paginación de listado de APIs
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas con portal activo: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El mock del portal responde:
  - `GET /apis?page=1` → `{"count": 25, "results": [/* 10 APIs */]}`
  - `GET /apis?page=2` → `{"count": 25, "results": [/* 10 APIs */]}`
  - `GET /apis?page=3` → `{"count": 25, "results": [/* 5 APIs */]}`

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| count_total | 25 | Total de APIs devuelto en el campo `count` |
| page_size | 10 | APIs por página (devueltas por el mock) |
| paginas_esperadas | 3 | Páginas necesarias para cubrir las 25 APIs |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Enviar `GET https://portal.example.com/apis?page=1` | El mock responde con `{"count": 25, "results": [10 APIs]}` |
| 2 | Sistema | Leer el campo `count=25` y determinar que necesita más páginas | El sistema solicita la página 2 |
| 3 | Sistema | Enviar `GET https://portal.example.com/apis?page=2` | El mock responde con `{"count": 25, "results": [10 APIs]}` |
| 4 | Sistema | Determinar que aún faltan APIs (20 de 25 descargadas) | El sistema solicita la página 3 |
| 5 | Sistema | Enviar `GET https://portal.example.com/apis?page=3` | El mock responde con `{"count": 25, "results": [5 APIs]}` |
| 6 | Sistema | Verificar que se han descargado 25 APIs (igual al `count`) | El proceso de paginación se detiene |
| 7 | Verificador (test) | Contar las APIs listadas en total | Se obtienen exactamente 25 APIs |

## Resultado esperado final

El sistema itera las páginas del portal hasta haber acumulado el número total de APIs indicado por el campo `count`. Se realizan exactamente 3 peticiones de listado (`page=1`, `page=2`, `page=3`) y se recuperan las 25 APIs.

## Observaciones

- Verificar que el sistema usa el campo `count` de la primera respuesta como referencia del total, no asume un número fijo de páginas.
- El parámetro de paginación en la URL debe ser `page=N` (no `offset`, no `cursor`).
