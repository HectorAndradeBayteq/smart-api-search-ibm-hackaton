# Reporte de trazabilidad — US-005-servidor-mcp-http

**Fecha:** 2026-08-28 18:10
**Rama:** feature/US-005-servidor-mcp-http
**Commit:** 0e845e4
**Trabajo:** [US-005](./README.md)
**Veredicto:** ⚠️ Aprobado con observaciones

## Resumen

Los 11 criterios quedan **Cubiertos**: 4 con pruebas automatizadas (AC críticos) y 7 con TC **Manual** por diseño, tras autorización de alcance (solo automatizar AC críticos). Ningún criterio en No cubierto.

**Pruebas:** caché de `quality-check` (commit 0e845e4, 2026-08-28). Resultado por suite: unit `PASS` · integration `N/A` · e2e `N/A`.

**Cobertura de criterios de aceptación**

| Total | Cubiertos | Parciales | No Cubiertos |
| ----- | --------- | --------- | ------------ |
| 11    | 11        | 0         | 0            |

## Cobertura por criterio

| Criterio | Descripción | Estado | Observaciones |
| -------- | ----------- | ------ | ------------- |
| AC-001 | Arranque uvicorn defaults + sin estado | Cubierto | TC-005 Manual por diseño (alcance autorizado) |
| AC-002 | Middleware GET → 405 | Cubierto | TC-003; suite efectiva unit (`ASGITransport`) |
| AC-003 | Formato search_openapi | Cubierto | TC-006 Manual por diseño |
| AC-004 | Formato get_endpoint_spec | Cubierto | TC-007 Manual por diseño |
| AC-005 | spec_ref inválido → ToolError | Cubierto | TC-004 automatizado |
| AC-006 | Prompt find_backend_api flujo | Cubierto | TC-008 Manual; registro también en TC-002 |
| AC-007 | Instrucciones del servidor | Cubierto | TC-009 Manual por diseño |
| AC-008 | ASGI / sin reexport | Cubierto | TC-001 automatizado |
| AC-009 | Tools+prompt en mcp de producción | Cubierto | TC-002 automatizado |
| AC-010 | Config clientes + start-server.ps1 | Cubierto | TC-010 Manual por diseño |
| AC-011 | README registro IBM Bob | Cubierto | TC-011 Manual por diseño |

## Matriz de trazabilidad

| Criterio | TC | Tipo | Evidencia | Ejecución | Resultado |
| -------- | -- | ---- | --------- | --------- | --------- |
| AC-001 | TC-005 | Manual | `test-cases/TC-005-arranque-defaults-stateless-manual.md` | Manual | N/A |
| AC-002 | TC-003 | Integration | `tests/test_server_asgi.py::test_middleware_get_returns_405` | quality-check | Paso |
| AC-003 | TC-006 | Manual | `test-cases/TC-006-search-openapi-formato-manual.md` | Manual | N/A |
| AC-004 | TC-007 | Manual | `test-cases/TC-007-get-endpoint-spec-formato-manual.md` | Manual | N/A |
| AC-005 | TC-004 | Unit | `tests/test_server_asgi.py::test_get_endpoint_spec_invalid_spec_ref_raises_tool_error` | quality-check | Paso |
| AC-006 | TC-008 | Manual | `test-cases/TC-008-prompt-flujo-manual.md` | Manual | N/A |
| AC-007 | TC-009 | Manual | `test-cases/TC-009-instructions-servidor-manual.md` | Manual | N/A |
| AC-008 | TC-001 | Unit | `tests/test_server_asgi.py::test_init_no_reexports_app` | quality-check | Paso |
| AC-009 | TC-002 | Unit | `tests/test_server_asgi.py::test_production_mcp_exposes_tools_and_prompt` | quality-check | Paso |
| AC-010 | TC-010 | Manual | `test-cases/TC-010-config-clientes-arranque-manual.md` | Manual | N/A |
| AC-011 | TC-011 | Manual | `test-cases/TC-011-readme-ibm-bob-manual.md` | Manual | N/A |

## Observaciones y pendientes

- Caveat de veredicto ⚠️: cobertura de AC-001, AC-003, AC-004, AC-006, AC-007, AC-010 y AC-011 apoyada en TCs **Manual por diseño** (autorizado: solo automatizar AC críticos).
- `work-integrate` acepta este ⚠️ y puede continuar el merge.

<!-- trace-validate:fingerprint=3b22afeda891fe49566cd5e3ffe3d1c084126467 · spec=6b90a5cdb2a92e6945a950f46f1115f74b10802d · generado=2026-08-28 -->
