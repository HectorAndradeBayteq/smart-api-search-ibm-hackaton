# US-004: Búsqueda híbrida de endpoints en lenguaje natural

**Estado:** Ready
**Fecha de creación:** 2025-07-19
**Última actualización:** 2025-07-19

## Descripción

**COMO** desarrollador que usa el sistema conectado a su IDE
**QUIERO** poder buscar endpoints de API en lenguaje natural mediante una consulta semántica híbrida con expansión HyDE y fusión RRF
**PARA** encontrar el endpoint más relevante sin conocer los nombres exactos de los paths ni leer documentación

## Contexto

La recuperación combina una rama densa (embeddings coseno) y una rama BM25 (dispersa), cuyos rankings se fusionan con RRF. La consulta puede expandirse opcionalmente con HyDE antes de generar el embedding denso, pero la rama BM25 siempre recibe el texto original sin modificar. Ingesta y recuperación usan exactamente el mismo modelo, dimensión y proveedor de embedding, definidos en la capa compartida.

El proveedor activo (`EMBED_PROVIDER=openai|watsonx`) y la dimensión correspondiente (`EMBED_DIM`) determinan tanto el vector denso que se genera en la búsqueda como el que se usó durante la ingesta; deben coincidir o la recuperación devolverá resultados incorrectos.

## Fuera de alcance

- Interfaz de usuario propia para la búsqueda (se expone vía servidor MCP, US-005).
- Gestión o actualización del índice vectorial (US-003).
- Consulta del spec completo de un endpoint concreto (cubierta por `get_endpoint_spec` en US-005).

## Referencias

- Ninguna por ahora

## Criterios de aceptación

- **AC-001 (Flujos de proceso):** El flujo de búsqueda DEBE seguir este orden: expansión HyDE opcional → embedding del texto expandido → prefetch denso y prefetch BM25 en paralelo → fusión RRF → devolver los `top_k` resultados con `1 ≤ top_k ≤ 10`.
- **AC-002 (Casos de uso):** HyDE DEBE poder desactivarse por configuración; cuando esté desactivado, el sistema DEBE embeberla consulta original y NO DEBE llamar al LLM.
- **AC-003 (Reglas de negocio):** La rama BM25 DEBE recibir siempre el contenido textual de la consulta original, sin reescritura ni expansión, envuelto en `Document(text=<texto_original>, model="Qdrant/bm25")`; la prohibición de expansión aplica al contenido textual, no a la envoltura técnica.
- **AC-004 (Salidas del sistema):** Cada resultado DEBE incluir: ranking, categoría, method, path, summary, description, definición consolidada, URL de llamada, deeplink, `spec_ref`, tags, origen, params y body.
- **AC-005 (Procesamiento de datos):** La URL de llamada DEBE ser la URL base del spec más el path del endpoint; NO DEBE ser la URL del portal ni el deeplink.
- **AC-006 (Procesamiento de datos):** Los params DEBEN incluir los declarados en la operación normalizados más los inferidos del template del path; DEBEN omitirse los parámetros sin nombre.
- **AC-007 (Procesamiento de datos):** El campo `spec_ref` DEBE tener el formato `source_file|METHOD|/path` con parseo estricto de exactamente tres segmentos no vacíos.
- **AC-008 (Fiabilidad):** La recuperación por referencia DEBE devolver vacío sin lanzar excepción si el punto no existe en la colección.
- **AC-009 (Idoneidad funcional):** Ingesta y recuperación DEBEN usar exactamente el mismo modelo, dimensión y función de embedding, definidos en la capa compartida; está PROHIBIDO definirlos en más de un lugar.
- **AC-010 (Integraciones):** La capa compartida de embeddings DEBE leer `EMBED_PROVIDER` desde la configuración y seleccionar el modelo y dimensión correspondientes: `text-embedding-3-large` / `EMBED_DIM=1024` para `openai`; `ibm/granite-embedding-278m-multilingual` / `EMBED_DIM=768` para `watsonx`.
- **AC-011 (Reglas de negocio):** Si el `EMBED_PROVIDER` o `EMBED_DIM` de la búsqueda no coinciden con los usados durante la ingesta, el sistema DEBERÍA advertir al operador; está PROHIBIDO que la búsqueda use un modelo o dimensión distintos a los de la colección activa sin advertencia.

---

## Complejidad sugerida

- **Story points:** 5
- **Justificación:** El flujo de búsqueda híbrida con HyDE y RRF requiere coordinar dos ramas de prefetch en paralelo, la fusión de rankings y la composición del resultado enriquecido. Complejidad moderada-alta reducida por la implementación previa.

## Repositorios

- smart-api-search-ibm-hackaton

## Validación

### INVEST

| Letra | Criterio      | Resultado | Notas |
| ----- | ------------- | --------- | ----- |
| **I** | Independiente | Parcial   | Depende de que la colección vectorial esté indexada (US-003), pero la lógica de recuperación puede implementarse y probarse con una colección de prueba. |
| **N** | Negociable    | Cumple    | El número de resultados `top_k`, el umbral de HyDE y el formato del resultado son negociables. |
| **V** | Valiosa       | Cumple    | Es la funcionalidad central del producto: la búsqueda en lenguaje natural. |
| **E** | Estimable     | Cumple    | Flujo bien definido, experiencia de la implementación previa disponible. |
| **S** | Cumple        | Cumple    | Alcance acotado a la capa de recuperación; no incluye servidor MCP ni ingesta. |
| **T** | Cumple        | Cumple    | Todos los criterios son verificables con colecciones de prueba y mocks de LLM. |

### Definition of Ready (DoR)

| Criterio DoR                       | Estado  | Notas |
| ---------------------------------- | ------- | ----- |
| Dependencias listas                | Cumple  | Qdrant Cloud disponible; la lógica de búsqueda puede probarse con una colección de prueba independientemente de US-003. |
| Inputs/outputs claros              | Cumple  | Entrada: texto de consulta + `top_k`. Salida: lista ordenada de resultados con todos los campos especificados. |
| Repositorios definidos             | Cumple  | smart-api-search-ibm-hackaton |
| Sin decisiones técnicas pendientes | Cumple  | Flujo, rama BM25, RRF, composición de resultado y capa compartida de embeddings están especificados. |
| Referencias de UI                  | No aplica | Sin UI propia; se expone vía herramienta MCP. |
| Sin aclaraciones pendientes        | Cumple  | Ninguna. |

## Observaciones

- La dependencia de US-003 afecta la dimensión **I** a `Parcial`; sin embargo, la capa de recuperación puede desarrollarse en paralelo usando una colección de prueba con datos sintéticos.
