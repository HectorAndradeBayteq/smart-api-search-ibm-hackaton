# TC-004 — Dado que IBM_PORTAL_AUTH=false e IBM_PORTAL_VERIFY_SSL=false, Cuando el sistema realiza llamadas al portal con certificado SSL no confiable, Entonces desactiva la verificación SSL y silencia los avisos de certificado

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Media
**Criterio de aceptación:** AC-003 (Integraciones) — Verificación SSL desactivada
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas: `IBM_PORTAL_VERIFY_SSL=false`, `IBM_PORTAL_AUTH=false`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El servidor mock del portal usa un certificado autofirmado (no confiable).
- El entorno de prueba permite capturar los warnings de urllib3/httpx relacionados con SSL.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_VERIFY_SSL | false | Desactiva la verificación del certificado SSL |
| IBM_PORTAL_AUTH | false | Sin autenticación IAM para simplificar el escenario |
| IBM_PORTAL_HOST | https://portal.example.com | Host con certificado autofirmado (mock) |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Iniciar el proceso de descubrimiento con `IBM_PORTAL_VERIFY_SSL=false` | El proceso arranca sin errores de configuración SSL |
| 2 | Sistema | Enviar `GET https://portal.example.com/apis?page=1` hacia el servidor con certificado autofirmado | La petición se completa con `200 OK` sin lanzar excepción por certificado |
| 3 | Verificador (test) | Capturar los warnings emitidos durante la ejecución (p. ej. `InsecureRequestWarning` de urllib3) | No se emite ningún aviso de certificado no confiable en la salida estándar ni en los logs |

## Resultado esperado final

El sistema completa las peticiones al portal sin fallos de SSL y sin emitir advertencias de certificado no confiable. La verificación SSL está desactivada en todos los clientes HTTP utilizados.

## Observaciones

- Verificar que la supresión del warning aplica tanto a urllib3 como a httpx si ambos se usan.
- Este TC no evalúa la seguridad del uso de `verify=False`; solo verifica que el comportamiento configurado se aplica correctamente.
