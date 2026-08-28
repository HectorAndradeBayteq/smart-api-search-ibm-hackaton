# TC-005 — Dado que IBM_PORTAL_VERIFY_SSL=true (por defecto), Cuando el sistema se conecta a un portal con certificado autofirmado, Entonces falla con error de certificado y no silencia el aviso

**Perspectiva:** Error
**Tipo de prueba:** Unit, Integration
**Prioridad:** Media
**Criterio de aceptación:** AC-003 (Integraciones) — Verificación SSL desactivada
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas: `IBM_PORTAL_VERIFY_SSL=true` (o variable ausente, asumiendo valor por defecto `true`), `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El servidor mock del portal usa un certificado autofirmado.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_VERIFY_SSL | true | Activa la verificación SSL (o variable ausente) |
| IBM_PORTAL_AUTH | false | Sin autenticación IAM para simplificar el escenario |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Iniciar el proceso de descubrimiento con `IBM_PORTAL_VERIFY_SSL=true` o sin definir la variable | El proceso intenta conectar al portal con verificación SSL activa |
| 2 | Sistema | Enviar `GET https://portal.example.com/apis?page=1` al servidor con certificado autofirmado | La petición falla con excepción de SSL (certificado no verificable) |
| 3 | Verificador (test) | Verificar que se emite un aviso o excepción de SSL | El sistema lanza o registra un error de verificación de certificado |

## Resultado esperado final

El sistema falla la petición al portal por error de verificación SSL. No se silencia el aviso de certificado no confiable cuando `IBM_PORTAL_VERIFY_SSL=true`. El proceso termina con un error comunicado de forma clara.

## Observaciones

- Este TC valida que `IBM_PORTAL_VERIFY_SSL=false` es condición necesaria para desactivar la verificación; el valor por defecto debe ser seguro (verificación activa).
