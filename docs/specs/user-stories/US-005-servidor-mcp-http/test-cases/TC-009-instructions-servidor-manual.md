# TC-009 — Dadas las instructions del servidor FastMCP, Cuando se revisan, Entonces prohíben buscar en workspace, traducir categorías y pegar JSON sin petición

**Perspectiva:** Happy Path
**Tipo de prueba:** Manual
**Prioridad:** Media
**Criterio de aceptación:** AC-007 — Instrucciones: usar KB del catálogo; no workspace; no traducir categorías; no pegar JSON salvo petición explícita
**Artefacto padre:** US-005
**Estado:** Ready
**Creado por:** Héctor Andrade
**Fecha:** 2026-08-28

## Precondiciones

- Instancia `FastMCP(..., instructions=...)` en `server.py`.

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Revisor | Leer el string `instructions` | Contiene las cuatro reglas de AC-007 |

## Resultado esperado final

Instrucciones conformes por inspección manual (alcance: sin assert automatizado para AC no críticos).
