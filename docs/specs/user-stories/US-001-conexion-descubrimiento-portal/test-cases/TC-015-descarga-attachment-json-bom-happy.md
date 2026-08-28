# TC-015 — Dado que el attachment de una API está en formato JSON con BOM, Cuando el sistema lo descarga, Entonces lo parsea correctamente ignorando el BOM inicial

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-008 (Integraciones) — Descarga de attachment OpenAPI (JSON/YAML, tolerando BOM)
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El mock del portal devuelve el attachment OpenAPI como un archivo JSON válido con BOM UTF-8 (`\xef\xbb\xbf`) al inicio.
- El sistema tiene configurado el portal con `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| formato_attachment | JSON con BOM UTF-8 | El archivo comienza con los bytes `EF BB BF` |
| contenido_ejemplo | `\xef\xbb\xbf{"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0"}}` | JSON válido con BOM al inicio |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Solicitar el attachment OpenAPI de una API al portal mock | El mock responde con el JSON con BOM |
| 2 | Sistema | Procesar el contenido del attachment | El BOM al inicio es ignorado/eliminado antes del parseo |
| 3 | Sistema | Parsear el JSON | El parseo se completa sin errores (`JSONDecodeError` u otros) |
| 4 | Verificador (test) | Verificar la estructura OpenAPI obtenida | El objeto parseado contiene `openapi: "3.0.0"` correctamente |

## Resultado esperado final

El sistema descarga y parsea correctamente el attachment OpenAPI en formato JSON con BOM. El documento OpenAPI resultante es válido y completo. No se producen errores de parseo por el BOM.

## Observaciones

- BOM UTF-8: bytes `\xef\xbb\xbf` al inicio del archivo.
- Verificar también el caso YAML con BOM (ver TC-016).
- El sistema NO debe reconstruir el spec desde `resources[]`; debe usar el attachment directamente.
