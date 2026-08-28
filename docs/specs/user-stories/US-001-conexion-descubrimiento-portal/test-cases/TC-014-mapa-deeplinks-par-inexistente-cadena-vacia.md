# TC-014 — Dado que el mapa de deeplinks está construido, Cuando se consulta un par (path, MÉTODO) que no existe en el mapa, Entonces el valor devuelto es cadena vacía

**Perspectiva:** Error
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-007 (Procesamiento de datos) — Mapa de deeplinks (path, MÉTODO) → URL
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El sistema ha construido el mapa de deeplinks con al menos un par conocido: `(GET, /payments/{id})`.
- Se consulta un par inexistente: `(DELETE, /payments/{id})`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| path_inexistente | /payments/{id} | Path presente en la API pero con método no definido |
| metodo_inexistente | DELETE | Método HTTP sin recurso deeplink para ese path |
| valor_esperado | "" (cadena vacía) | Resultado para clave inexistente |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Construir el mapa de deeplinks con el par `(GET, /payments/{id})` | Mapa construido correctamente |
| 2 | Verificador (test) | Consultar el mapa con la clave `(DELETE, /payments/{id})` | El mapa devuelve cadena vacía `""` |
| 3 | Verificador (test) | Verificar que no se lanza excepción (KeyError u otra) | La consulta devuelve `""` sin error |

## Resultado esperado final

La consulta de un par `(path, MÉTODO)` inexistente en el mapa devuelve cadena vacía `""`. No se lanza ninguna excepción. El sistema gestiona claves ausentes de forma controlada.

## Observaciones

- La semántica de «cadena vacía» debe ser `""` (string vacío), no `None`, no `None` omitido.
- Verificar también con un path completamente nuevo (no solo método diferente).
