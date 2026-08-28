---
name: Estándares de Testing
domain: testing
status: Active
last_update: 2025-07-14
source_adrs: [ADR-004]
tags: [pytest, mypy, ruff, coverage, integration, quality-gate]
---

# Estándares de Testing

Este estándar cubre las normas del dominio de calidad y pruebas del proyecto `smart-api-search`. Aplica a la estructura de pruebas, las herramientas de análisis estático, la cobertura mínima y la separación de pruebas unitarias e integración. Define la compuerta de calidad que debe pasar el proyecto antes de cualquier entrega.

## Pruebas unitarias con pytest

**ID:** pruebas-unitarias
**Estado:** Active

Las pruebas unitarias **DEBEN** implementarse con **pytest**. La cobertura de código en las capas de dominio (`src/smart_api_search/`) **DEBE** ser **≥ 80%**, con umbrales mínimos por módulo declarados en `pyproject.toml` (`[tool.coverage.report]`). La suite completa de pruebas unitarias **DEBE** ejecutarse sin credenciales externas ni servicios en red.

La configuración de pytest (`pytest.ini_options`) **DEBE** estar en `pyproject.toml`. La directiva `fail_under = 80` en `[tool.coverage.report]` hace que el check de cobertura sea bloqueante.

### Excepciones

Los módulos de configuración, entrypoints ASGI y código de arranque pueden quedar excluidos de la cobertura mínima si se justifica en `pyproject.toml` mediante `omit`.

## Pruebas de integración: marcado y exclusión por defecto

**ID:** pruebas-integracion
**Estado:** Active

Las pruebas de integración (aquellas que requieren credenciales reales o servicios en red como Qdrant Cloud u OpenAI) **DEBEN** marcarse con el decorador `@pytest.mark.integration`. Las pruebas de integración **DEBEN** estar excluidas del run por defecto de pytest (configurado con `-m "not integration"` en `addopts` de `pyproject.toml`). Ejecutarlas requiere invocación explícita con `-m integration` y un entorno con las credenciales configuradas.

### Excepciones

Ninguna. Si una prueba requiere un servicio externo, debe estar marcada con `@pytest.mark.integration`.

## Análisis estático: mypy estricto

**ID:** mypy-estricto
**Estado:** Active

El proyecto **DEBE** pasar la verificación de tipos con **mypy** en modo estricto (`strict = true` en `[tool.mypy]` de `pyproject.toml`). Ningún archivo del paquete `smart_api_search` **DEBE** emitir errores de tipo al ejecutar `mypy src/`.

### Excepciones

Las dependencias de terceros sin stubs pueden ignorarse con `ignore_missing_imports = true` para ese paquete específico, documentado en `pyproject.toml`.

## Linter y formatter: ruff

**ID:** ruff-linter-formatter
**Estado:** Active

El proyecto **DEBE** usar **ruff** como linter y formatter. La ejecución de `ruff check .` y `ruff format --check .` **DEBE** completarse sin diferencias ni errores. La longitud de línea máxima **DEBE** ser de **100 caracteres** (`line-length = 100` en `[tool.ruff]`).

### Excepciones

Ninguna.

## Criterios de cumplimiento

| ID | Requisito | Descripción | Origen | Automatizable | Enfoque | Verificación |
|----|-----------|-------------|--------|---------------|---------|--------------|
| CR-001 | pruebas-unitarias | La cobertura en capas de dominio **DEBE** ser ≥ 80% | [ADR-004](../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md) | yes | bloqueante | no |
| CR-002 | pruebas-integracion | Las pruebas de integración **DEBEN** marcarse con `@pytest.mark.integration` y excluirse del run por defecto | [ADR-004](../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md) | yes | bloqueante | no |
| CR-003 | mypy-estricto | `mypy src/` **DEBE** ejecutarse sin errores con `strict = true` | [ADR-004](../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md) | yes | bloqueante | no |
| CR-004 | ruff-linter-formatter | `ruff check .` y `ruff format --check .` **DEBEN** completarse sin diferencias | [ADR-004](../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md) | yes | bloqueante | no |

## Referencias

- [ADR-004: Compuerta de calidad: pytest, ruff, mypy estricto, coverage ≥ 80%](../adr/ADR-004-compuerta-calidad-pytest-mypy-ruff.md)
- [SRS-001: smart-api-search](../requirements/SRS-001-smart-api-search.md)
