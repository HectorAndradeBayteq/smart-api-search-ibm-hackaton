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

- [ ] **IT-01** — Implementar prueba de vectores duales simultáneos
  Con mock de `QdrantClient.upsert`, llamar a `index_operation` con una operación de prueba. Capturar el argumento `points` de la llamada a `upsert`. Afirmar que el punto contiene exactamente los dos vectores nombrados esperados (denso y disperso) y que ninguno de los dos es `None`.
- [ ] **IT-02** — Implementar prueba del tipo del objeto disperso al indexar y al consultar
  Al indexar: usar el mismo punto capturado en IT-01; afirmar que el valor en la rama dispersa del punto es instancia de `models.Document`. Al consultar: con mock de `QdrantClient.query_points`, llamar al método de búsqueda (implementado en US-004 / capa de búsqueda); capturar el argumento de la rama BM25 en el prefetch y afirmar que es instancia de `models.Document`. Si la capa de búsqueda no está disponible, esta sub-parte queda como observación de dependencia futura pero la prueba de indexación no se bloquea.
- [ ] **IT-03** — Implementar prueba de ingesta multi-operación por la misma fuente
  Construir un conjunto de al menos tres operaciones con el mismo `source_file`. Con mock del cliente Qdrant que reporta esa fuente como no existente (nuevo), invocar el orquestador de ingesta. Verificar que `upsert` se llamó exactamente tres veces (una por operación), no solo una.
- [ ] **IT-04** — Implementar prueba de coherencia de recuento al finalizar la ingesta
  Con mock de `QdrantClient.count` que devuelve el valor esperado, ejecutar el orquestador de ingesta sobre N operaciones de prueba. Verificar que el sistema llama a `count` al final de la ejecución y que compara el recuento obtenido con el número de operaciones indexadas; si hay discrepancia, la prueba debe fallar (o el orquestador debe emitir una advertencia capturable).
