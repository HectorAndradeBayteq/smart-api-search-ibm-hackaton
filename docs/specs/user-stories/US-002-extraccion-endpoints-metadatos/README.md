# US-002: Extracción de endpoints y metadatos de presentación

**Estado:** Ready
**Fecha de creación:** 2025-07-19
**Última actualización:** 2025-07-19

## Descripción

**COMO** desarrollador que usa el sistema de búsqueda de APIs
**QUIERO** que el sistema extraiga las operaciones de cada spec OpenAPI/Swagger y aplique metadatos de presentación por categoría
**PARA** disponer de un conjunto de operaciones enriquecido con contexto de presentación listo para indexar y buscar

## Contexto

La unidad de indexación es la operación OpenAPI (par `path` + método HTTP), no el archivo completo. Los metadatos de presentación por categoría se leen de un archivo versionado bajo `config/` y permiten personalizar el título y la descripción de cada categoría de APIs antes de presentar resultados.

## Fuera de alcance

- Generación de embeddings o indexación en la base vectorial (US-003).
- Presentación final de resultados al usuario (US-004 y US-005).

## Referencias

- Ninguna por ahora

## Criterios de aceptación

- **AC-001 (Procesamiento de datos):** El sistema DEBE recorrer la sección `paths` del spec y extraer los métodos HTTP estándar presentes (`get`, `post`, `put`, `delete`, `patch`, `head`, `options`, `trace`), normalizados a mayúsculas.
- **AC-002 (Procesamiento de datos):** El sistema DEBE soportar tanto OpenAPI 3.x como Swagger 2.0; en Swagger 2.0 DEBE componer la URL base concatenando `schemes`, `host` y `basePath`.
- **AC-003 (Procesamiento de datos):** Ante specs con información escasa, el sistema DEBE obtener texto útil aplicando la cadena de respaldo: `summary` → primera línea de `description` → `operationId` → descripciones de parámetros; DEBE usar la primera alternativa no vacía.
- **AC-004 (Procesamiento de datos):** El sistema DEBE conservar por operación un fragmento crudo JSON que incluya: información del spec, servidor base, formato, path, method y el objeto operation completo; este fragmento DEBE estar disponible para la herramienta de consulta de spec.
- **AC-005 (Procesamiento de datos):** Si un spec no declara la sección `paths`, el sistema DEBE generar un documento marcador para esa API de modo que no desaparezca en silencio del índice.
- **AC-006 (Procesamiento de datos):** El sistema DEBE aplicar una función de limpieza de texto (macros, admoniciones, espacios redundantes) tanto al indexar como al presentar resultados; el texto limpio DEBE ser idéntico en ambas rutas.
- **AC-007 (Integraciones):** DEBE existir un archivo versionado bajo `config/` que permita definir, de forma opcional y por categoría, un título y una descripción de presentación.
- **AC-008 (Procesamiento de datos):** Si una categoría no define metadatos en el archivo de `config/`, el sistema DEBE usar el título y la descripción del propio spec como valores de presentación.
- **AC-009 (Fiabilidad):** Si el archivo de configuración de categorías no existe o tiene sintaxis inválida, el proceso DEBE fallar al arrancar, antes de procesar ningún spec, indicando la ruta del archivo y la causa del error.

---

## Complejidad sugerida

- **Story points:** 3
- **Justificación:** Parseo de dos versiones OpenAPI, cadena de respaldo de texto y archivo de configuración de categorías son cambios bien acotados. La implementación previa reduce incertidumbre.

## Repositorios

- smart-api-search-ibm-hackaton

## Validación

### INVEST

| Letra | Criterio      | Resultado | Notas |
| ----- | ------------- | --------- | ----- |
| **I** | Independiente | Cumple    | Depende del spec descargado (US-001) o del archivo local (US-003), pero la lógica de extracción y metadatos es independiente de cómo llegó el spec. |
| **N** | Negociable    | Cumple    | La cadena de respaldo de texto y el esquema del archivo de configuración son negociables en detalle. |
| **V** | Valiosa       | Cumple    | Sin extracción no hay operaciones que indexar; sin metadatos de categoría la presentación pierde contexto. |
| **E** | Estimable     | Cumple    | Requisitos claros y completos; la implementación previa confirma la estimación. |
| **S** | Pequeña       | Cumple    | Alcance acotado a extracción y metadatos; no incluye embeddings ni servidor. |
| **T** | Testeable     | Cumple    | Todos los criterios son verificables con specs de prueba locales sin dependencias externas. |

### Definition of Ready (DoR)

| Criterio DoR                       | Estado   | Notas |
| ---------------------------------- | -------- | ----- |
| Dependencias listas                | Cumple   | No tiene dependencias bloqueantes; el spec puede llegar de portal o de archivo local. |
| Inputs/outputs claros              | Cumple   | Entradas: spec OpenAPI (JSON/YAML) + archivo de config de categorías. Salidas: lista de operaciones extraídas con fragmento crudo y metadatos de presentación. |
| Repositorios definidos             | Cumple   | smart-api-search-ibm-hackaton |
| Sin decisiones técnicas pendientes | Cumple   | Formato del archivo de config, cadena de respaldo y manejo de specs sin paths están especificados. |
| Referencias de UI                  | No aplica | No hay UI propia. |
| Sin aclaraciones pendientes        | Cumple   | Ninguna. |

## Observaciones

- Ninguna.
