# TK-004: Pruebas de verificabilidad del pipeline

**Estado:** Ready
**Historia:** [US-003](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar las cuatro pruebas de verificabilidad obligatorias derivadas de los criterios de fiabilidad de la historia, todas con mock de los servicios externos (sin llamadas reales a Qdrant ni al LLM): (1) inspeccionar el argumento del punto enviado a la escritura en Qdrant y afirmar la presencia simultánea de los dos vectores nombrados (denso y disperso); (2) afirmar que el tipo del objeto entregado en la rama dispersa es `models.Document`, tanto al indexar como al consultar; (3) ejecutar el pipeline con varias operaciones de la misma fuente y verificar que todas se indexan (no solo la primera); (4) verificar al final de la ingesta que el recuento de puntos confirmados por Qdrant es coherente con el número de operaciones extraídas.

## Dependencias

- TK-001 — `ensure_collection()`, `shared.get_embedding()` disponibles
- TK-002 — `enrich_operation()`, `index_operation()` disponibles
- TK-003 — lógica de idempotencia y orquestador de ingesta disponibles
- `pytest` ≥ 8.2 — framework de pruebas
- `pytest-asyncio` — pruebas de código async si aplica
- `unittest.mock` (stdlib) — mocks del cliente Qdrant, LLM y embeddings

## Referencias

- **Arquitectura:** [ADR-002: Qdrant Cloud como base vectorial](../../../adr/ADR-002-qdrant-cloud-base-vectorial.md)
- **Arquitectura:** [ADR-010: Inferencia de vectores dispersos delegada al motor](../../../adr/ADR-010-inferencia-vectores-dispersos-motor.md)
- **Arquitectura:** [ADR-012: Idempotencia de ingesta con granularidad de fuente](../../../adr/ADR-012-idempotencia-ingesta-granularidad-fuente.md)
- **Arquitectura:** [ADR-005: Unidad de indexación es la operación OpenAPI](../../../adr/ADR-005-unidad-indexacion-operacion-openapi.md)

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── tests/
    └── + test_verificabilidad.py   # cuatro pruebas de verificabilidad obligatorias (AC-021 a AC-024)
```

## Plan de implementación

- [x] **IT-01** — AC-021 cubierto en `tests/test_pipeline.py::test_index_operation_writes_both_vectors`
- [x] **IT-02** — AC-022 cubierto en `tests/test_pipeline.py::test_index_operation_sparse_is_document`
- [x] **IT-03** — AC-023 cubierto en `tests/test_verificabilidad.py::test_multi_operation_same_source_all_indexed`
- [x] **IT-04** — AC-024 cubierto en `tests/test_verificabilidad.py::test_count_coherence_after_ingestion`
