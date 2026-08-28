# TC-016 — Dado que el attachment de una API está en formato YAML con BOM, Cuando el sistema lo descarga, Entonces lo parsea correctamente ignorando el BOM inicial

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-008 (Integraciones) — Descarga de attachment OpenAPI (JSON/YAML, tolerando BOM)
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El mock del portal devuelve el attachment OpenAPI como un archivo YAML válido con BOM UTF-8 (`\xef\xbb\xbf`) al inicio.
- El sistema tiene configurado el portal con `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| formato_attachment | YAML con BOM UTF-8 | El archivo YAML comienza con los bytes `EF BB BF` |
| contenido_ejemplo | `\xef\xbb\xbfopenapi: "3.0.0"\ninfo:\n  title: Test\n  version: "1.0"` | YAML válido con BOM al inicio |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Solicitar el attachment OpenAPI de una API al portal mock (YAML con BOM) | El mock responde con el YAML con BOM |
| 2 | Sistema | Procesar el contenido del attachment | El BOM al inicio es ignorado/eliminado antes del parseo |
| 3 | Sistema | Parsear el YAML | El parseo se completa sin errores |
| 4 | Verificador (test) | Verificar la estructura OpenAPI obtenida | El objeto parseado contiene `openapi: "3.0.0"` correctamente |

## Resultado esperado final

El sistema descarga y parsea correctamente el attachment OpenAPI en formato YAML con BOM. El documento OpenAPI resultante es válido y completo. No se producen errores de parseo por el BOM.

## Observaciones

- Complementario al TC-015 para JSON con BOM.
- Verificar que el sistema detecta automáticamente el formato (JSON vs YAML) o lo infiere del Content-Type.
- El sistema NO debe reconstruir el spec desde `resources[]`; debe usar el attachment directamente.
