# TC-012 — Dado que el portal devuelve APIs con slugs duplicados, Cuando el sistema asigna source_name, Entonces añade sufijo numérico para que cada source_name sea único

**Perspectiva:** Error
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-006 (Procesamiento de datos) — source_name estable portal:{slug}
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El sistema recibe una lista de 3 APIs donde dos tienen el mismo slug: `payments-api`, `payments-api`, `payments-api`.
- El entorno de prueba es unitario, sin conexión al portal real.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| slug_api_1 | payments-api | Primera ocurrencia del slug |
| slug_api_2 | payments-api | Segunda ocurrencia duplicada |
| slug_api_3 | payments-api | Tercera ocurrencia duplicada |
| source_names_esperados | portal:payments-api, portal:payments-api-2, portal:payments-api-3 | Sufijos numéricos para desambiguar |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Procesar la lista de 3 APIs con slug `payments-api` | El sistema detecta los duplicados |
| 2 | Verificador (test) | Comprobar el `source_name` de la primera API | Es `portal:payments-api` (sin sufijo) |
| 3 | Verificador (test) | Comprobar el `source_name` de la segunda API | Es `portal:payments-api-2` (sufijo `-2`) |
| 4 | Verificador (test) | Comprobar el `source_name` de la tercera API | Es `portal:payments-api-3` (sufijo `-3`) |
| 5 | Verificador (test) | Verificar que todos los source_name son únicos | No hay dos fuentes con el mismo identificador |

## Resultado esperado final

El sistema asigna `portal:payments-api` a la primera ocurrencia y `portal:payments-api-2`, `portal:payments-api-3` a las siguientes, garantizando unicidad. Los sufijos son numéricos y se incrementan secuencialmente.

## Observaciones

- Verificar el esquema de sufijo exacto: `-2`, `-3`, etc. (o `_2`, `_3` si así lo define la implementación; alinear con el criterio AC-006).
- El sufijo debe añadirse solo cuando hay duplicados; el primero no debe tener sufijo.
