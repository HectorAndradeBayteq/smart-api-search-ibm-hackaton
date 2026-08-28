---
version: "1.0"
last_update: 2025-07-14
---

# Definition of Done — smart-api-search

Criterios que debe satisfacer **cualquier unidad de trabajo** (historia de usuario, tarea técnica o
tarea de mantenimiento) antes de considerarse cerrada. Ningún criterio es opcional; las excepciones
se documentan explícitamente y con justificación en el artefacto de trabajo correspondiente.

> **Origen:** Anexo B del SRS-001 identifica la ausencia de una Definition of Done como deuda de
> proceso de la primera implementación. Este documento la cubre.

---

## 1. Código

| # | Criterio |
|---|----------|
| C-01 | El código compila / el paquete se instala sin errores (`pip install -e .`). |
| C-02 | No hay errores de tipado: `mypy src/` pasa en modo estricto (`strict = true`). |
| C-03 | No hay errores ni diferencias de formato: `ruff check .` y `ruff format --check .` pasan sin salida. |
| C-04 | Ninguna credencial, URL de servicio ni valor de `EMBED_DIM` aparece literal en el código ni en archivos versionados (RNF-06). |
| C-05 | La capa compartida (`smart_api_search.shared`) es la única que importa los clientes de embeddings; ningún otro módulo los importa directamente (RNF-07, ADR-009). |

## 2. Pruebas

| # | Criterio |
|---|----------|
| T-01 | Las pruebas unitarias pasan: `pytest -m "not integration"` termina en verde. |
| T-02 | La cobertura en las capas de dominio es ≥ 80 % (`pytest --cov` con `fail_under = 80`). |
| T-03 | Toda prueba que llame a un servicio externo real está marcada con `@pytest.mark.integration` y queda excluida del run por defecto (ADR-004, CR-002). |
| T-04 | Cada requisito con símbolo ⚠ en el SRS tiene al menos una prueba que ancla el comportamiento: si se revierte la corrección, la prueba falla (RF-V.6). |
| T-05 | Existe una prueba sobre el objeto ASGI de producción (`smart_api_search.server:app`) que afirma que expone las dos herramientas y el prompt (RF-V.4). *(aplica solo cuando el módulo de servidor esté implementado)* |

## 3. Arquitectura

| # | Criterio |
|---|----------|
| A-01 | Toda decisión nueva o modificada está registrada como ADR en `docs/adr/` con estado `Accepted` y enlazada desde `docs/adr/README.md`. |
| A-02 | Si el ADR emite requisitos de estándar, esos requisitos existen en el archivo de estándar de dominio correspondiente en `docs/standards/`. |
| A-03 | El estándar de retrieval (CR sobre `EMBED_DIM`) no tiene contradicciones: un solo valor por proveedor, declarado una sola vez en `.env`. |

## 4. Trazabilidad

| # | Criterio |
|---|----------|
| TR-01 | Cada criterio de aceptación (AC-XXX) de la historia o tarea tiene al menos un caso de prueba (TC-XXX) asociado. |
| TR-02 | El `progress.md` de la historia/tarea refleja todas las unidades en estado `Done` antes del merge. |
| TR-03 | El estado de la historia/tarea en `docs/specs/` está alineado con su `progress.md` al cerrar. |

## 5. Proceso

| # | Criterio |
|---|----------|
| P-01 | La rama de trabajo ha sido publicada en el remoto al menos una vez antes del merge (Anexo B — deuda "trabajo sin publicar"). |
| P-02 | El merge se hace hacia la rama desde la que se creó la rama de trabajo, sin commits de merge no revisados. |
| P-03 | El mensaje de commit sigue Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) con scope cuando aplica. |

---

## Notas de aplicación

- **Proyectos nuevos sin servidor implementado:** el criterio T-05 se marca N/A hasta que
  `smart_api_search.server` exista.
- **Excepciones de cobertura:** los módulos excluidos en `[tool.coverage.run] omit` de
  `pyproject.toml` quedan fuera del umbral; deben estar justificados en ese mismo archivo.
- **Integración con arch-audit:** los criterios A-01..A-03 son verificables automáticamente
  con `arch-audit` antes del merge.
