# TC-022 — Dado que las variables del portal no están definidas, Cuando se ejecuta la suite de pruebas, Entonces los tests pasan sin errores de configuración del portal

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit, Integration
**Prioridad:** Alta
**Criterio de aceptación:** AC-010 (Fiabilidad) — Opcionalidad de configuración del portal en tiempo de carga
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- Ninguna de las variables del portal está definida en el entorno de ejecución de la suite de pruebas: `IBM_PORTAL_HOST`, `IBM_PORTAL_AUTH`, `IBM_TOKEN_URL`, `IBM_INSTANCE_ID`, `IBM_API_KEY`, `IBM_PORTAL_VERIFY_SSL` están ausentes.
- Los tests del portal (los que sí necesitan esas variables) usan mocks o están marcados para saltar si las variables están ausentes.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| IBM_PORTAL_HOST | (ausente) | Variable de portal no definida en el entorno CI |
| IBM_API_KEY | (ausente) | Variable de portal no definida en el entorno CI |
| entorno | CI sin credenciales de portal | Simula un entorno de integración continua sin acceso al portal real |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Ingeniero/CI | Ejecutar la suite de pruebas completa (`pytest`) sin variables del portal en el entorno | La suite comienza a ejecutarse |
| 2 | Suite de pruebas | Cargar los módulos del sistema (incluidos los del portal) | Los módulos se importan sin lanzar excepciones por variables ausentes |
| 3 | Suite de pruebas | Ejecutar los tests que no requieren el portal (unitarios, modo archivos) | Los tests pasan correctamente |
| 4 | Verificador (test) | Verificar el resultado de la suite | No hay fallos por ausencia de variables del portal (los tests de integración con portal real se marcan como skipped si las variables están ausentes) |

## Resultado esperado final

La suite de pruebas se ejecuta hasta completarse sin fallos causados por la ausencia de variables del portal. Los módulos del portal se pueden importar y los tests que no requieren el portal real pasan correctamente. Los tests de integración que necesitan el portal real están marcados con skip condicional.

## Observaciones

- La carga del módulo del portal (import) no debe ejecutar conexiones reales ni validar variables de entorno en tiempo de importación.
- Alineado con el comentario de validación INVEST en la US-001: «AC-010 requiere prueba de arranque en modo archivos».
