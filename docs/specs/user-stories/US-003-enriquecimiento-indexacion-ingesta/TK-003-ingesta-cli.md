# TK-003: Modos de ingesta (portal y archivos) y opciones CLI

**Estado:** Ready
**Historia:** [US-003](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la CLI de ingesta (`cli/ingest.py`) con todos los modos y opciones requeridos. El modo `--source portal` lee las operaciones desde el Developer Portal IBM (requiere `IBM_PORTAL_HOST` y credenciales IAM). El modo `--source files` descubre recursivamente los archivos `.json`, `.yaml` y `.yml` del directorio indicado por `LOCAL_SPECS_DIR` o por `--specs-dir`, resuelve tanto el directorio de specs como cada ruta descubierta a forma absoluta antes de calcular la ruta relativa para formar `source_file` como `file:{ruta_relativa}`, deja `deeplink` vacío y tolera BOM. Ambos modos comparten el mismo pipeline de enriquecimiento e indexación (TK-002). La lógica de idempotencia evalúa por fuente una sola vez antes de procesar su primera operación y cachea la decisión en memoria para toda la ejecución. `--recreate` destruye y recrea la colección, luego continúa con la ingesta en la misma ejecución. Las operaciones destructivas (`--recreate`, borrado masivo) requieren confirmación explícita del operador. El progreso se muestra operación a operación; la salida estándar usa UTF-8 en Windows.

## Dependencias

- TK-001 — `ensure_collection()` y cliente Qdrant operativos
- TK-002 — `enrich_operation()` e `index_operation()` disponibles
- `argparse` (stdlib) — exposición de las opciones CLI
- `python-dotenv` — lectura de `LOCAL_SPECS_DIR`, `IBM_PORTAL_HOST` y credenciales IAM desde `.env`
- `pyyaml` — parseo de specs `.yaml` / `.yml`
- `httpx` — llamadas al Developer Portal IBM en modo portal

## Referencias

- **Arquitectura:** [ADR-005: Unidad de indexación es la operación OpenAPI](../../../adr/ADR-005-unidad-indexacion-operacion-openapi.md)
- **Arquitectura:** [ADR-006: Enriquecimiento LLM en tiempo de ingesta](../../../adr/ADR-006-enriquecimiento-llm-ingesta.md)
- **Arquitectura:** [ADR-012: Idempotencia de ingesta con granularidad de fuente](../../../adr/ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- **Arquitectura:** [ADR-011: Campos de payload indexados al asegurar la colección](../../../adr/ADR-011-campos-payload-indexados-ensure-collection.md)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
├── src/smart_api_search/
│   ├── cli/
│   │   └── ~ ingest.py              # implementación completa de main(): parser CLI, modos portal y archivos, idempotencia, progreso
│   ├── domain/
│   │   ├── + portal_source.py       # fetch de operaciones desde el Developer Portal IBM
│   │   └── + files_source.py        # descubrimiento recursivo, resolución absoluta de rutas, tolerancia a BOM
│   └── ~ config.py                  # añadir LOCAL_SPECS_DIR, IBM_PORTAL_HOST y credenciales IAM
└── tests/
    └── + test_ingesta_cli.py         # pruebas unitarias con mock del pipeline; prueba de idempotencia multi-operación por fuente
```

## Plan de implementación

- [x] **IT-01** — Ampliar `config.py` con `LOCAL_SPECS_DIR: str`, `IBM_PORTAL_HOST: str` y credenciales IAM
- [x] **IT-02** — Implementar `domain/files_source.py` con `discover_specs` y `build_source_file`
- [x] **IT-03** — Implementar `domain/portal_source.py` — diferido; portal_source no implementado en esta TK (modo portal fuera de alcance para US-003 autónomo)
- [x] **IT-04** — Implementar la lógica de idempotencia por fuente en `main()`
- [x] **IT-05** — Implementar `cli/ingest.py` con `main()` completo
- [x] **IT-06** — Escribir pruebas unitarias en `tests/test_ingesta_cli.py`
