---
name: Estándares de DevOps
domain: devops
status: Active
last_update: 2025-07-14
source_adrs: [ADR-003]
tags: [python, pip, venv, powershell, toolchain, pyproject]
---

# Estándares de DevOps

Este estándar cubre las normas del dominio de infraestructura y DevOps del proyecto `smart-api-search`. Aplica al toolchain de Python, la gestión de dependencias, el entorno de ejecución y los scripts de arranque. Define las reglas que garantizan la reproducibilidad del entorno de desarrollo y la portabilidad de la instalación.

## Toolchain Python y entorno de desarrollo

**ID:** toolchain-python
**Estado:** Active

El proyecto **DEBE** usar **Python 3.12** como runtime. Las dependencias **DEBEN** aislarse en un entorno virtual `.venv` en la raíz del repositorio. Las dependencias de producción **DEBEN** fijarse con el operador `==` en `pyproject.toml` para garantizar reproducibilidad. Las dependencias de desarrollo (herramientas de calidad, testing) **DEBEN** declararse en `requirements-dev.txt`.

La herramienta de gestión de paquetes es **pip**. Los scripts de arranque del servidor y del entorno **DEBEN** escribirse en **PowerShell (.ps1)**, que es el shell de referencia del entorno de desarrollo del proyecto.

El `pyproject.toml` **DEBE** usar `setuptools.build_meta` como backend de build.

### Excepciones

En entornos CI/CD con Linux, los scripts `.ps1` pueden adaptarse o reemplazarse por equivalentes shell si el runner no dispone de PowerShell. En ese caso, la adaptación debe documentarse.

## Criterios de cumplimiento

| ID | Requisito | Descripción | Origen | Automatizable | Enfoque | Verificación |
|----|-----------|-------------|--------|---------------|---------|--------------|
| CR-001 | toolchain-python | El proyecto **DEBE** usar Python 3.12 como runtime | [ADR-003](../adr/ADR-003-python312-pip-venv-toolchain.md) | yes | bloqueante | no |
| CR-002 | toolchain-python | Las dependencias de producción **DEBEN** fijarse con `==` en `pyproject.toml` | [ADR-003](../adr/ADR-003-python312-pip-venv-toolchain.md) | yes | bloqueante | no |

## Referencias

- [ADR-003: Python 3.12, pip y entorno virtual como toolchain](../adr/ADR-003-python312-pip-venv-toolchain.md)
- [pyproject.toml del proyecto](../../pyproject.toml)
