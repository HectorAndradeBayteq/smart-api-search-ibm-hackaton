# TC-007 — Dado que el portal devuelve count=0, Cuando el sistema lista las APIs, Entonces no solicita ninguna página adicional y devuelve lista vacía

**Perspectiva:** Límite
**Tipo de prueba:** Unit
**Prioridad:** Media
**Criterio de aceptación:** AC-004 (Integraciones) — Paginación de listado de APIs
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas con portal activo: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El mock del portal responde a `GET /apis?page=1` con `{"count": 0, "results": []}`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| count_total | 0 | Total de APIs devuelto: portal sin APIs publicadas |
| respuesta_page1 | `{"count": 0, "results": []}` | Única respuesta del mock |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Enviar `GET https://portal.example.com/apis?page=1` | El mock responde con `{"count": 0, "results": []}` |
| 2 | Sistema | Leer el campo `count=0` | El sistema determina que no hay APIs y no solicita más páginas |
| 3 | Verificador (test) | Verificar el número de peticiones realizadas al portal | Solo se realizó 1 petición (`page=1`); no se solicitó `page=2` |
| 4 | Verificador (test) | Verificar la lista de APIs obtenida | Lista vacía, sin errores |

## Resultado esperado final

El sistema devuelve una lista vacía de APIs sin errores y sin realizar peticiones adicionales al portal. Solo se ejecutó una petición de listado (`page=1`).

## Observaciones

- Caso límite donde `count=0` es el valor mínimo posible del campo de total.
