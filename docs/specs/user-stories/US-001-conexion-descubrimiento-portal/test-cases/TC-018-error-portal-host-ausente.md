# TC-018 — Dado que la variable IBM_PORTAL_HOST está ausente, Cuando el sistema intenta iniciar el descubrimiento del portal, Entonces falla con mensaje claro y sin traza técnica

**Perspectiva:** Error
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-009 (Casos de uso) — Mensajes de error claros sin traza técnica
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- La variable de entorno `IBM_PORTAL_HOST` no está definida en el entorno.
- El resto de variables del portal pueden estar definidas o no; `IBM_PORTAL_HOST` es la única ausente que aplica a este TC.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_HOST | (ausente) [propuesto] | Variable crítica no definida |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Intentar iniciar el proceso de descubrimiento del portal sin `IBM_PORTAL_HOST` | El sistema detecta la ausencia de la variable |
| 2 | Sistema | Emitir el mensaje de error | El mensaje indica claramente que `IBM_PORTAL_HOST` es requerida y no está configurada |
| 3 | Verificador (test) | Inspeccionar la salida del sistema | El mensaje es legible, no contiene stack trace, nombre de clase interna ni traceback de Python |
| 4 | Verificador (test) | Verificar que el proceso termina de forma controlada | No se lanza excepción no capturada al nivel de usuario |

## Resultado esperado final

El sistema emite un mensaje de error del tipo «Falta la variable de entorno requerida: IBM_PORTAL_HOST» y termina el proceso de descubrimiento de forma controlada. No se imprime ningún stack trace ni información técnica interna (traceback, nombre de módulo, línea de código).

## Observaciones

- El mensaje debe ser comprensible para un operador sin conocimiento del código fuente.
- Verificar que el sistema tampoco imprime el stack trace en modo debug activo en producción.
