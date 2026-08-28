# TC-003 — Dado que IBM_PORTAL_AUTH=false, Cuando el sistema inicia el descubrimiento del portal, Entonces no solicita token ni envía cabecera Authorization

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-002 (Integraciones) — Modo sin autenticación
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas: `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- Las variables `IBM_TOKEN_URL`, `IBM_INSTANCE_ID` e `IBM_API_KEY` están vacías o ausentes.
- El servidor mock del portal responde con `200 OK` a llamadas sin cabecera de autenticación.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_AUTH | false | Desactiva el flujo IAM |
| IBM_TOKEN_URL | (vacío) [propuesto] | Debe poder estar ausente sin errores |
| IBM_INSTANCE_ID | (vacío) [propuesto] | Debe poder estar ausente sin errores |
| IBM_API_KEY | (vacío) [propuesto] | Debe poder estar ausente sin errores |
| IBM_PORTAL_HOST | https://portal.example.com | Host del portal (mock) |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Iniciar el proceso de descubrimiento con `IBM_PORTAL_AUTH=false` y sin variables IAM | El proceso arranca sin errores de configuración |
| 2 | Sistema | Enviar `GET https://portal.example.com/apis?page=1` | La petición no incluye cabecera `Authorization` |
| 3 | Verificador (test) | Inspeccionar todas las peticiones HTTP capturadas al portal | Ninguna petición contiene cabecera `Authorization` |
| 4 | Verificador (test) | Verificar que no se realizó ninguna llamada a ninguna URL IAM | El mock IAM no registra ninguna petición entrante |

## Resultado esperado final

El sistema completa el descubrimiento sin errores. No se realizan peticiones a la URL de token IAM. Ninguna petición al portal incluye la cabecera `Authorization`. Las variables IAM pueden estar vacías o ausentes sin provocar ningún error.

## Observaciones

- Cubrir también el escenario en que `IBM_TOKEN_URL` y `IBM_INSTANCE_ID` están definidas pero `IBM_PORTAL_AUTH=false`: deben ignorarse igualmente.
