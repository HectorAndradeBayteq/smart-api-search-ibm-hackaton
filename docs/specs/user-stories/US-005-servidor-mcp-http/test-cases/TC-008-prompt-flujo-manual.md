# TC-008 — Dado el prompt find_backend_api, Cuando se lee su plantilla, Entonces guía buscar → presentar → pedir spec solo si el usuario lo solicita

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-006 — DEBE existir prompt find_backend_api(need) con flujo buscar → presentar → pedir spec solo si se solicita
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Prompt registrado (verificado también por TC-002 automatizado).
- Validación del texto del flujo por revisión manual (alcance autorizado).

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Leer `find_backend_api` en `server.py` | Instrucciones ES/EN con pasos 1–3 |
| 2 | Revisor | Confirmar gate antes de `get_endpoint_spec` | Solo tras petición explícita del usuario |

## Resultado esperado final

Contenido del prompt conforme a AC-006; registro automatizado cubierto por TC-002.
