---
id: ADR-003
status: Accepted
last_update: 2025-07-14
deciders: [Equipo]
tags: [python, pip, venv, powershell, devops, toolchain]
supersedes: null
superseded_by: null
emits: [devops/CR-001, devops/CR-002]
---

# ADR-003: Python 3.12, pip y entorno virtual como toolchain

## Contexto

El proyecto se desarrolla en Windows para el hackathon IBM. Se requiere un toolchain de Python reproducible, con dependencias aisladas y scripts de arranque compatibles con el entorno de desarrollo del equipo. La elección del gestor de paquetes y del entorno afecta la portabilidad y la reproducibilidad de la instalación.

## Decisión

Usar **Python 3.12** como runtime, **pip** como gestor de paquetes, **entorno virtual `.venv`** para el aislamiento de dependencias, y dependencias de producción fijadas con `==` en `pyproject.toml`. Los scripts de arranque se escriben en **PowerShell (.ps1)**. Las dependencias de desarrollo (herramientas de calidad, testing) se declaran en `requirements-dev.txt`.

## Alternativas consideradas

- **Poetry**: overhead de gestión de lockfile para un proyecto de hackathon; complejidad adicional sin beneficio proporcional.
- **uv**: excelente rendimiento pero menos universal en entornos corporativos Windows en el momento del hackathon.
- **conda**: excesivo para este contexto; introduce una capa de gestión de entornos más pesada que la necesaria.

## Consecuencias

### Positivas

- Python 3.12 es la versión LTS más reciente con soporte completo para `StrEnum`, tipado estricto y mejoras de rendimiento.
- pip + `.venv` es el toolchain estándar de Python, ampliamente conocido y sin dependencias adicionales.
- PowerShell es el shell nativo de Windows y el entorno de referencia del equipo.

### Negativas / trade-offs

- Las dependencias fijadas con `==` requieren actualización manual para recibir parches de seguridad.
- `requirements-dev.txt` separado de `pyproject.toml` requiere mantener dos ficheros de dependencias.
- Los scripts `.ps1` no son portables directamente a macOS/Linux sin ajuste.

## Referencias

- [Estándar DevOps](../standards/devops.md)
- [pyproject.toml del proyecto](../../pyproject.toml)
