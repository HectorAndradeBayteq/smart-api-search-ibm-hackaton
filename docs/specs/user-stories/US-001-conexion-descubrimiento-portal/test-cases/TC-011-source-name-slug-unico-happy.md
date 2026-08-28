# TC-011 — Dado que el portal devuelve APIs con slugs únicos, Cuando el sistema asigna source_name, Entonces cada fuente recibe el identificador portal:{slug} estable

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-006 (Procesamiento de datos) — source_name estable portal:{slug}
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El sistema recibe una lista de APIs con slugs únicos: `payments-api`, `users-api`, `inventory-api`.
- No hay duplicados en los slugs de la lista.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| slug_1 | payments-api | Slug único de la primera API |
| slug_2 | users-api | Slug único de la segunda API |
| slug_3 | inventory-api | Slug único de la tercera API |
| source_name_esperado_1 | portal:payments-api | Formato esperado |
| source_name_esperado_2 | portal:users-api | Formato esperado |
| source_name_esperado_3 | portal:inventory-api | Formato esperado |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Procesar la lista de APIs con slugs únicos | El sistema asigna un `source_name` a cada API |
| 2 | Verificador (test) | Comprobar el `source_name` de la primera API | Es `portal:payments-api` |
| 3 | Verificador (test) | Comprobar el `source_name` de la segunda API | Es `portal:users-api` |
| 4 | Verificador (test) | Comprobar el `source_name` de la tercera API | Es `portal:inventory-api` |
| 5 | Verificador (test) | Ejecutar el proceso dos veces con los mismos datos | Los `source_name` son idénticos en ambas ejecuciones (estabilidad) |

## Resultado esperado final

Cada API recibe un `source_name` con el formato exacto `portal:{slug}`, siendo idéntico en sucesivas ejecuciones con los mismos datos de entrada (estabilidad). No se añaden sufijos cuando los slugs son únicos.

## Observaciones

- La estabilidad del `source_name` es crítica para no romper referencias externas entre ejecuciones del descubrimiento.
