# TK-002: Limpieza de texto y marcador para specs sin paths

**Estado:** Ready
**Historia:** [US-002](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la función de limpieza de texto reutilizable tanto en la ruta de indexación como en la de presentación de resultados, garantizando salida idéntica en ambas rutas. La función elimina macros de documentación (p. ej. `{{% note %}}`, `{{< warning >}}`), admoniciones RST/Markdown (`.. note::`, `.. warning::`, `!!! note`) y espacios redundantes (tabulaciones, múltiples espacios o saltos de línea consecutivos). Además, implementar la generación de un documento marcador para specs que no declaren la sección `paths`, de modo que no desaparezcan en silencio del índice.

## Dependencias

- `src/smart_api_search/cli/ingest.py` — módulo donde se implementan las funciones; `clean_text` debe ser importable desde aquí para usarse también en la capa de presentación de resultados
- TK-001 (parser de operaciones) — `clean_text` se aplica sobre el texto extraído por `extract_operations`; TK-001 debe estar disponible antes de integrar la limpieza en el flujo

## Referencias

- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-01](../../technical-docs/smart-api-search.md#md-01) — MD-01 (QdrantPoint): campo `description` debe contener texto limpio; campo `summary` también se limpia tras la cadena de respaldo
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — paso 6 del flujo FL-01: limpieza de texto aplicada en indexación; paso 5: si el spec no tiene `paths`, genera documento marcador

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    └── ~ cli/ingest.py                          # clean_text(), make_marker_document()
tests/
    └── + test_text_cleaning.py                  # Pruebas: macros, admoniciones, espacios, idempotencia, marcador sin paths
```

## Plan de implementación

- [x] **IT-01** — Implementar función `clean_text(text: str) -> str` que aplica la limpieza en este orden: (a) eliminar macros de plantilla tipo Hugo/Jinja (`{{% … %}}`, `{{< … >}}`, `{{ … }}`); (b) eliminar bloques de admonición RST (`.. note::`, `.. warning::`, `.. tip::`, etc.) y Markdown (`!!! note`, `!!! warning`); (c) colapsar espacios internos múltiples (incluidos tabulaciones) en un solo espacio; (d) colapsar saltos de línea consecutivos (tres o más) en dos; (e) hacer `strip()` al resultado
  La función debe ser pura (sin efectos secundarios) y su salida debe ser idéntica si se aplica dos veces sobre el mismo input (idempotente)
- [x] **IT-02** — Integrar `clean_text` en `extract_operations` (TK-001): aplicar sobre los campos `summary` y `description` del dict parcial de QdrantPoint tras la cadena de respaldo, antes de construir el punto final
  El mismo módulo (`cli/ingest.py`) exporta `clean_text` para que la capa de presentación de resultados (US-005) pueda importarla y producir exactamente el mismo texto limpio
- [x] **IT-03** — Implementar función `make_marker_document(spec: dict, source_file: str, fmt: str) -> dict` que genera un dict parcial de QdrantPoint marcador cuando el spec no declara `paths` (o `paths` está vacío)
  Campos obligatorios del marcador: `source_file`, `spec_format`, `api_title` (desde `spec["info"]["title"]`), `api_version`, `api_description`; `method` = `"MARKER"`, `path` = `"/"`, `spec_ref` = `source_file|MARKER|/`, `summary` = `"(no paths declared)"`, `raw_spec` = fragmento mínimo con `info` y `format`
- [x] **IT-04** — Integrar `make_marker_document` en el flujo principal de `ingest.py`: después de parsear un spec, si `paths` está ausente o vacío, llamar a `make_marker_document` en lugar de `extract_operations`; el marcador pasa por el mismo pipeline de indexación que una operación normal
- [x] **IT-05** — Escribir pruebas unitarias en `tests/test_text_cleaning.py`
  Cubrir: macro Hugo eliminada, admonición RST eliminada, admonición Markdown eliminada, múltiples espacios colapsados, saltos de línea excesivos colapsados, texto limpio que no cambia al aplicar dos veces (`clean_text(clean_text(x)) == clean_text(x)`), texto vacío devuelve cadena vacía, `make_marker_document` con spec sin `paths` (campos obligatorios presentes y `method="MARKER"`), `make_marker_document` con spec con `paths: {}` vacío
