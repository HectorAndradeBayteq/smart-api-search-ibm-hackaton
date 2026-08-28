# TC-021 — Dado que las variables del portal no están definidas, Cuando el sistema arranca en modo archivos, Entonces inicia correctamente sin errores de configuración del portal

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-010 (Fiabilidad) — Opcionalidad de configuración del portal en tiempo de carga
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Ninguna de las variables del portal está definida en el entorno: `IBM_PORTAL_HOST`, `IBM_PORTAL_AUTH`, `IBM_TOKEN_URL`, `IBM_INSTANCE_ID`, `IBM_API_KEY`, `IBM_PORTAL_VERIFY_SSL` están ausentes.
- El servidor MCP está configurado para operar en modo archivos (fuente de datos local, sin portal).

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_HOST | (ausente) | Variable de portal no definida |
| IBM_PORTAL_AUTH | (ausente) | Variable de portal no definida |
| IBM_API_KEY | (ausente) | Variable de portal no definida |
| modo_operacion | archivos | El servidor usa fuentes locales, no el portal |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Iniciar el servidor MCP en modo archivos sin ninguna variable del portal definida | El servidor arranca sin errores |
| 2 | Verificador (test) | Verificar los logs de arranque del servidor | No hay errores ni advertencias relacionados con variables del portal |
| 3 | Verificador (test) | Comprobar que el servidor responde a peticiones de búsqueda en modo archivos | El servidor procesa peticiones correctamente usando la fuente de datos local |

## Resultado esperado final

El servidor MCP arranca correctamente en modo archivos sin que la ausencia de variables del portal cause ningún error o excepción. El sistema funciona con normalidad para las operaciones que no requieren el portal.

## Observaciones

- Este TC es crítico para el arranque en CI/CD sin credenciales de portal configuradas.
- Relacionado con AC-010: las variables del portal deben ser opcionales en tiempo de carga del módulo.
