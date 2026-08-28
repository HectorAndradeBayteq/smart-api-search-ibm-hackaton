# TC-019 — Dado que IBM_PORTAL_AUTH=true e IBM_API_KEY está ausente, Cuando el sistema intenta iniciar la autenticación IAM, Entonces falla con mensaje claro y sin traza técnica

**Perspectiva:** Error
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-009 (Casos de uso) — Mensajes de error claros sin traza técnica
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Variables de entorno configuradas: `IBM_PORTAL_AUTH=true`, `IBM_PORTAL_HOST=https://portal.example.com`, `IBM_TOKEN_URL=https://iam.example.com`, `IBM_INSTANCE_ID=inst-001`.
- La variable `IBM_API_KEY` no está definida en el entorno.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_AUTH | true | Autenticación activa |
| IBM_API_KEY | (ausente) [propuesto] | Clave de API no definida |
| IBM_PORTAL_HOST | https://portal.example.com | Host del portal definido |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Intentar iniciar el proceso de descubrimiento con `IBM_PORTAL_AUTH=true` y sin `IBM_API_KEY` | El sistema detecta la ausencia de la clave de API |
| 2 | Sistema | Emitir el mensaje de error | El mensaje indica claramente que `IBM_API_KEY` es requerida cuando la autenticación está activa |
| 3 | Verificador (test) | Inspeccionar la salida del sistema | El mensaje es legible, no contiene stack trace ni traceback de Python |
| 4 | Verificador (test) | Verificar que no se realizó ninguna petición al servidor IAM | El proceso termina antes de intentar obtener el token |

## Resultado esperado final

El sistema emite un mensaje de error del tipo «Falta la variable de entorno requerida: IBM_API_KEY (autenticación activa)» y termina el proceso de descubrimiento sin intentar contactar el servidor IAM. No se imprime ningún stack trace.

## Observaciones

- El mensaje debe indicar explícitamente que la razón de la exigencia es que `IBM_PORTAL_AUTH=true`.
- Relacionado con AC-001 y AC-002: la validación de presencia de `IBM_API_KEY` solo aplica cuando `IBM_PORTAL_AUTH=true`.
