# Reporte de trazabilidad — US-001

**Trabajo:** US-001 — Conexión y descubrimiento de APIs en el Developer Portal
**Rama:** `feature/US-001-conexion-descubrimiento-portal`
**Fecha:** 2025-07-21
**Generado por:** trace-validate

---

## Resumen

Pruebas: resultados reutilizados de la corrida de `quality-check` del commit `85b388f`.
— Suite `unit`: PASS (34 passed) · Suite `integration`: N/A (excluida por defecto, ADR-004) · Suite `e2e`: N/A (sin config)

| Criterios de aceptación | Cubiertos | Parciales | No cubiertos |
|-------------------------|-----------|-----------|--------------|
| 10 | 8 | 2 | 0 |

---

## Cobertura por criterio

| Criterio | Descripción | Estado | Observaciones |
|----------|-------------|--------|---------------|
| AC-001 | Auth IAM: obtener token y enviar cabecera `Authorization: bearer` | ⚠️ Parcial | TC-001 y TC-002 declaran `Unit, Integration`. La parte `Unit` está automatizada y pasó. La parte `Integration` no tiene artefacto automatizado (ADR-004 la excluye por defecto). |
| AC-002 | Sin auth: no solicitar token ni enviar cabecera | ⚠️ Parcial | TC-003 declara `Unit, Integration`. `Unit` automatizada y pasó. `Integration` sin artefacto (ADR-004). |
| AC-003 | SSL desactivado: `verify=False` y silenciar avisos | ⚠️ Parcial | TC-004 declara `Unit, Integration`. TC-005 declara `Unit, Integration`. Partes `Unit` automatizadas y pasaron. Partes `Integration` sin artefacto (ADR-004). |
| AC-004 | Paginación `GET /apis?page=N` hasta cubrir `count` | ✅ Cubierto | TC-006 (`Unit`) y TC-007 (`Unit`) automatizados y pasaron. |
| AC-005 | Detalle en paralelo máx 12, fallo parcial no aborta | ✅ Cubierto | TC-008 (`Unit`), TC-009 (`Unit`), TC-010 (`Unit`) automatizados y pasaron. |
| AC-006 | `source_name` estable `portal:{slug}` con sufijo ante duplicados | ✅ Cubierto | TC-011 (`Unit`) y TC-012 (`Unit`) automatizados y pasaron. |
| AC-007 | Mapa deeplinks `(path, MÉTODO) → URL`, cadena vacía si falta | ✅ Cubierto | TC-013 (`Unit`) y TC-014 (`Unit`) automatizados y pasaron. |
| AC-008 | Attachment JSON/YAML tolerando BOM; no reconstruir desde `resources[]` | ⚠️ Parcial | TC-015, TC-016, TC-017 declaran `Unit, Integration`. Partes `Unit` automatizadas y pasaron. Partes `Integration` sin artefacto (ADR-004). |
| AC-009 | Errores claros sin traza técnica ante configuración faltante o API sin attachment | ✅ Cubierto | TC-018 (`Unit`), TC-019 (`Unit`), TC-020 (`Unit`) automatizados y pasaron. |
| AC-010 | Variables de portal opcionales en tiempo de carga (no bloquea modo archivos ni pytest) | ✅ Cubierto | TC-021 (`Unit`) y TC-022 (`Unit`) automatizados y pasaron. |

---

## Matriz de trazabilidad

| Criterio | TC | Tipo | Evidencia | Ejecución | Resultado |
|----------|----|------|-----------|-----------|-----------|
| AC-001 | TC-001 | Unit | `tests/test_portal_client.py::test_get_iam_token_returns_access_token`, `test_build_portal_client_with_auth_includes_authorization_header` | quality-check | Paso |
| AC-001 | TC-001 | Integration | — | — | No cubierto |
| AC-001 | TC-002 | Unit | `tests/test_portal_client.py::test_get_iam_token_raises_on_missing_access_token` | quality-check | Paso |
| AC-001 | TC-002 | Integration | — | — | No cubierto |
| AC-002 | TC-003 | Unit | `tests/test_portal_client.py::test_build_portal_client_without_auth_has_no_authorization_header`, `test_build_portal_client_without_auth_does_not_call_iam` | quality-check | Paso |
| AC-002 | TC-003 | Integration | — | — | No cubierto |
| AC-003 | TC-004 | Unit | `tests/test_portal_client.py::test_build_portal_client_ssl_disabled_uses_verify_false`, `test_build_portal_client_ssl_disabled_suppresses_warnings` | quality-check | Paso |
| AC-003 | TC-004 | Integration | — | — | No cubierto |
| AC-003 | TC-005 | Unit | — | — | No cubierto |
| AC-003 | TC-005 | Integration | — | — | No cubierto |
| AC-004 | TC-006 | Unit | `tests/test_portal_discovery.py::test_list_all_apis_multiple_pages`, `test_list_all_apis_single_page` | quality-check | Paso |
| AC-004 | TC-006 | Integration | — | — | No cubierto |
| AC-004 | TC-007 | Unit | `tests/test_portal_discovery.py::test_list_all_apis_count_zero`, `test_list_all_apis_raises_on_missing_count` | quality-check | Paso |
| AC-005 | TC-008 | Unit | `tests/test_portal_discovery.py::test_fetch_api_details_preserves_order` | quality-check | Paso |
| AC-005 | TC-008 | Integration | — | — | No cubierto |
| AC-005 | TC-009 | Unit | `tests/test_portal_discovery.py::test_fetch_api_details_partial_failure_returns_none` | quality-check | Paso |
| AC-005 | TC-009 | Integration | — | — | No cubierto |
| AC-005 | TC-010 | Unit | `tests/test_portal_discovery.py::test_fetch_api_details_respects_concurrency_limit` | quality-check | Paso |
| AC-006 | TC-011 | Unit | `tests/test_portal_processing.py::test_assign_source_name_unique_slugs`, `test_assign_source_name_stable_across_calls` | quality-check | Paso |
| AC-006 | TC-012 | Unit | `tests/test_portal_processing.py::test_assign_source_name_two_duplicate_slugs`, `test_assign_source_name_three_duplicate_slugs`, `test_assign_source_name_all_unique_after_dedup` | quality-check | Paso |
| AC-007 | TC-013 | Unit | `tests/test_portal_processing.py::test_build_deeplink_map_existing_pair_returns_url`, `test_build_deeplink_map_method_stored_uppercase` | quality-check | Paso |
| AC-007 | TC-014 | Unit | `tests/test_portal_processing.py::test_build_deeplink_map_missing_pair_returns_empty_string`, `test_build_deeplink_map_completely_new_path_returns_empty_string`, `test_build_deeplink_map_empty_resources_returns_empty_dict` | quality-check | Paso |
| AC-008 | TC-015 | Unit | `tests/test_portal_discovery.py::test_download_attachment_json_with_bom` | quality-check | Paso |
| AC-008 | TC-015 | Integration | — | — | No cubierto |
| AC-008 | TC-016 | Unit | `tests/test_portal_discovery.py::test_download_attachment_yaml_with_bom` | quality-check | Paso |
| AC-008 | TC-016 | Integration | — | — | No cubierto |
| AC-008 | TC-017 | Unit | `tests/test_portal_discovery.py::test_download_attachment_raises_on_missing_attachment` | quality-check | Paso |
| AC-008 | TC-017 | Integration | — | — | No cubierto |
| AC-009 | TC-018 | Unit | `tests/test_portal_client.py::test_build_portal_client_raises_on_missing_portal_host` | quality-check | Paso |
| AC-009 | TC-019 | Unit | `tests/test_portal_client.py::test_build_portal_client_raises_on_missing_api_key_with_auth` | quality-check | Paso |
| AC-009 | TC-020 | Unit | `tests/test_portal_processing.py::test_process_attachment_error_logs_and_continues` | quality-check | Paso |
| AC-009 | TC-020 | Integration | — | — | No cubierto |
| AC-010 | TC-021 | Unit | `tests/test_portal_client.py::test_settings_instantiable_without_portal_vars` | quality-check | Paso |
| AC-010 | TC-021 | Integration | — | — | No cubierto |
| AC-010 | TC-022 | Unit | `tests/test_portal_client.py::test_module_importable_without_portal_vars` | quality-check | Paso |
| AC-010 | TC-022 | Integration | — | — | No cubierto |

---

## Observaciones y pendientes

- **Partes `Integration` sin automatizar (AC-001 a AC-003, AC-005 a AC-010):** Los TCs que declaran tipo `Integration` no tienen artefacto automatizado. Según ADR-004, las pruebas de integración se marcan con `@pytest.mark.integration` y se ejecutan explícitamente en entornos con credenciales reales; se excluyen de la suite por defecto. Los criterios afectados se reportan **Parcial** por esta razón, no por defecto de implementación.
- **TC-005 (`Unit` y `Integration`) sin artefacto:** Este TC verifica SSL activo con certificado autofirmado. La verificación real requiere un servidor con cert autofirmado — escenario de integración. El criterio AC-003 se sostiene por TC-004 (Unit), que sí está automatizado.

---

## Veredicto: ⚠️ Aprobado con observaciones

Ningún criterio en `No cubierto`. 2 criterios en `Parcial` (AC-001 y AC-002; los demás en Parcial también son por Integration no automatizada, que es por diseño per ADR-004). Las partes `Unit` de todos los criterios pasaron. Las pruebas de integración están excluidas por diseño y deben ejecutarse con credenciales reales en entorno CI.

<!-- trace-validate:fingerprint=64a7ae7da050c6c0f4707ed9b65bcfe3a9d61437 · spec=5aae44db76e900378b3f0978726bfc8972452f86 · generado=2025-07-21 -->
