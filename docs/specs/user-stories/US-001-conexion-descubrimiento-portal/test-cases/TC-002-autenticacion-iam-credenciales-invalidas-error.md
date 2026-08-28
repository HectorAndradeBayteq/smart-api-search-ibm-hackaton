# TC-002 — Dado que IBM_PORTAL_AUTH=true y la clave de API es inválida, Cuando el sistema solicita el token IAM, Entonces falla con mensaje claro y sin traza técnica

**Perspectiva:** Error
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-001 (Integraciones) — Autenticación IAM con token
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas: `IBM_PORTAL_AUTH=true`, `IBM_TOKEN_URL=https://iam.example.com`, `IBM_INSTANCE_ID=inst-001`, `IBM_API_KEY=invalid-key`, `IBM_PORTAL_HOST=https://portal.example.com`.
- El servidor mock IAM responde con `401 Unauthorized` al recibir la clave inválida.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_AUTH | true | Activa el flujo IAM |
| IBM_API_KEY | invalid-key [propuesto] | Clave de API inválida o revocada |
| respuesta_mock | 401 Unauthorized | Respuesta del servidor IAM ante clave incorrecta |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Iniciar el proceso de descubrimiento con `IBM_API_KEY=invalid-key` | El proceso intenta obtener el token IAM |
| 2 | Sistema | Enviar `POST https://iam.example.com/inst-001/apikeys/token` con la clave inválida | El mock IAM responde `401 Unauthorized` |
| 3 | Sistema | Procesar la respuesta de error del servidor IAM | El proceso termina con un mensaje de error legible |
| 4 | Verificador (test) | Comprobar el mensaje de error emitido | El mensaje describe el fallo de autenticación sin incluir stack trace ni detalles internos |

## Resultado esperado final

El proceso falla con un mensaje claro que indica que la autenticación IAM falló (p. ej.: «Error al obtener el token IAM: credenciales inválidas»). No se imprime ningún stack trace ni información técnica interna. No se realizan llamadas posteriores al portal.

## Observaciones

- Relacionado con AC-009: el formato del mensaje de error debe cumplir también los criterios de ese AC.
- Verificar que el proceso no continúa con llamadas al portal tras el fallo de autenticación.
