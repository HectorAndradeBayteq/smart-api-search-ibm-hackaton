# TC-001 — Dado el paquete smart_api_search importado, Cuando se inspeccionan sus símbolos exportados, Entonces __init__.py no reexporta app ni ningún símbolo de server.py

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-008 — El servidor DEBE exponerse mediante la referencia ASGI del módulo; el paquete NO DEBE reexportar símbolos que sombreen a sus propios submódulos
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2025-08-28

## Precondiciones

- El módulo `smart_api_search` instalado en el entorno de desarrollo (editable install).
- `smart_api_search/__init__.py` en su estado de producción.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| módulo inspeccionado | `smart_api_search` | Importado directamente |
| símbolo prohibido | `app` | No debe estar en `dir(smart_api_search)` |
| símbolo prohibido | `server` (re-export) | No debe importarse desde `__init__` |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Test | Importar `import smart_api_search` | Sin error de importación |
| 2 | Test | Evaluar `hasattr(smart_api_search, 'app')` | `False` |
| 3 | Test | Evaluar `hasattr(smart_api_search, 'server')` como re-export | `False` (no debe exponer la aplicación ASGI vía `__init__`) |

## Resultado esperado final

`smart_api_search.__init__` no expone ni `app` ni ningún símbolo proveniente de `smart_api_search.server`. El paquete se importa limpio sin efectos secundarios sobre el módulo servidor.

## Observaciones

Cubre el ADR-013: reexportar `app` en `__init__.py` provoca doble carga del módulo con uvicorn, resultando en un servidor sin herramientas. Esta prueba verifica la condición estructural que lo previene. Independiente de credenciales externas.
