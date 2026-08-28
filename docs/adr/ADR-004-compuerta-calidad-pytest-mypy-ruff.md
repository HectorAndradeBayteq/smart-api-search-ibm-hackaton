---
id: ADR-004
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [pytest, mypy, ruff, coverage, testing, quality-gate]
supersedes: null
superseded_by: null
emits: [testing/CR-001, testing/CR-002, testing/CR-003, testing/CR-004]
---

# ADR-004: Compuerta de calidad: pytest, ruff, mypy estricto, coverage ≥ 80%

## Contexto

Los requisitos no funcionales RNF-01..RNF-07 del SRS establecen umbrales de calidad para el proyecto. La implementación anterior pasó todos los checks de CI pero falló en producción por falta de pruebas de integración real, evidenciando que la compuerta debe incluir checks de verificabilidad (RF-V.1..V.7). Se necesita definir el conjunto de herramientas y umbrales que forman la compuerta de calidad del proyecto.

## Decisión

La compuerta de calidad del proyecto consiste en:

- **pytest**: ejecución de pruebas unitarias.
- **Cobertura ≥ 80%** en capas de dominio, con mínimo por módulo declarado en `pyproject.toml`.
- **mypy** en modo estricto (`strict = true`).
- **ruff** como linter y formatter (sin diferencias toleradas).
- Las pruebas de integración se marcan con `@pytest.mark.integration` y se **excluyen del run por defecto**; se ejecutan explícitamente en entornos con credenciales reales.

Sin API testing en la fase inicial del proyecto.

## Alternativas consideradas

- **flake8 + black**: dos herramientas separadas para lo que ruff unifica; overhead innecesario.
- **pylint**: más lento y con mayor número de falsos positivos que ruff para este stack.
- **bandit** (análisis de seguridad): valorado pero no incluido en la fase inicial del hackathon.

## Consecuencias

### Positivas

- Compuerta unificada y ejecutable con un solo comando (`pytest --cov`).
- mypy estricto previene errores de tipos en tiempo de desarrollo.
- ruff garantiza estilo consistente con mínima configuración.
- La separación `@pytest.mark.integration` permite ejecutar solo unitarios en local sin credenciales.

### Negativas / trade-offs

- mypy estricto puede requerir anotaciones adicionales en código legacy o de terceros.
- La exclusión por defecto de pruebas de integración significa que algunos fallos solo se detectan en CI o con credenciales reales.
- Coverage ≥ 80% en capas de dominio puede ser difícil de mantener si la lógica tiene ramas complejas de manejo de errores.

## Referencias

- [Estándar Testing](../standards/testing.md)
- [SRS-001: smart-api-search](../requirements/SRS-001-smart-api-search.md)
