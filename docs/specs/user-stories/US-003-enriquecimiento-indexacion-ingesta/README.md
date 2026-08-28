# US-003: Enriquecimiento LLM, indexación híbrida e ingesta desde archivos locales

**Estado:** Ready
**Fecha de creación:** 2025-07-19
**Última actualización:** 2025-07-19

## Descripción

**COMO** operador del sistema que necesita mantener el catálogo de APIs actualizado
**QUIERO** que el sistema enriquezca cada operación con un texto generado por LLM y la indexe en la colección vectorial híbrida, tanto desde el Developer Portal como desde archivos OpenAPI locales
**PARA** que la base vectorial contenga representaciones semánticas ricas que permitan búsquedas precisas en lenguaje natural

## Contexto

La colección vectorial es híbrida: contiene un vector denso (coseno, dimensión `EMBED_DIM`) y un vector disperso (BM25). Ambos vectores deben escribirse simultáneamente en cada punto. El enriquecimiento LLM puede omitirse con `--no-enrich` para ingestas rápidas. La idempotencia de ingesta se evalúa una sola vez por fuente, antes de procesar su primera operación.

El proveedor de embeddings es configurable mediante `EMBED_PROVIDER` (`.env`): `openai` usa `text-embedding-3-large` truncado a 1024 dimensiones; `watsonx` usa `ibm/granite-embedding-278m-multilingual` con 768 dimensiones. `EMBED_DIM` debe declararse una sola vez en `.env` con el valor correspondiente al proveedor activo; cambiar de proveedor invalida la colección y obliga a reindexar.

El modo archivos (`--source files`) lee specs OpenAPI/Swagger de un directorio local y comparte el mismo pipeline de enriquecimiento e indexación que el modo portal; las diferencias son solo en cómo se obtiene el spec y cómo se forma el `source_file`.

## Reglas de negocio

- **BR-01:** El sistema DEBE escribir siempre los dos vectores (denso y disperso) en el mismo punto; está PROHIBIDO escribir un punto con solo uno de los dos vectores. → verificado por AC-004
- **BR-02:** La generación del vector disperso DEBE delegarse al motor de vectores; el cliente DEBE entregar el texto envuelto en el objeto de documento que el motor exige, tanto al indexar como al consultar. → verificado por AC-005
- **BR-03:** Todo campo de payload usado como criterio de filtro DEBE tener un índice de tipo `keyword` creado de forma idempotente al asegurar la colección; como mínimo `source_file` y `spec_ref`. → verificado por AC-008
- **BR-04:** La decisión de omitir o indexar una fuente DEBE tomarse una sola vez por fuente y antes de procesar su primera operación, y DEBE permanecer constante durante toda la ejecución. → verificado por AC-009
- **BR-05:** `--recreate` DEBE recrear la colección y DEBE continuar con la ingesta en la misma ejecución, informando al final cuántos puntos indexó; NO DEBE terminar dejando la colección vacía. → verificado por AC-012
- **BR-06:** El directorio de specs y las rutas descubiertas DEBEN resolverse ambos a forma absoluta antes de calcular la ruta relativa para formar el `source_file`. → verificado por AC-017

## Referencias

- Ninguna por ahora

## Criterios de aceptación

- **AC-001 (Integraciones):** La colección DEBE ser híbrida: vector denso con métrica coseno y dimensión `EMBED_DIM` más vector disperso BM25 con modificador IDF.
- **AC-002 (Procesamiento de datos):** El sistema DEBE enriquecer cada operación llamando al LLM para generar un texto en inglés de 250–400 palabras que incluya propósito, capacidades, casos de uso, una línea `Keywords:` y una sección `Example questions users might ask:`.
- **AC-003 (Casos de uso):** La CLI DEBE ofrecer la opción `--no-enrich` que indexa los metadatos del spec sin llamar al LLM.
- **AC-004 (Procesamiento de datos):** Cada punto escrito DEBE contener simultáneamente el vector denso y el vector disperso; está PROHIBIDO escribir un punto con un solo vector.
- **AC-005 (Integraciones):** La generación del vector disperso DEBE delegarse al motor Qdrant; el texto DEBE entregarse envuelto en `Document(text=<texto>, model="Qdrant/bm25")`, tanto al indexar como al consultar; está PROHIBIDO enviar el texto como cadena simple.
- **AC-006 (Procesamiento de datos):** El texto indexable DEBE componerse como: cabecera compacta `[categoría | API | formato | método path | tags | base]` más el texto enriquecido; el deeplink NO DEBE formar parte del texto embebido.
- **AC-007 (Procesamiento de datos):** El payload de cada punto DEBE incluir al menos: `api_title`, `api_version`, `api_description`, `category`, `method`, `path`, `summary`, `description`, `tags`, `operationId`, `environment`, `server_url`, `spec_format`, `source_file`, `enriched_text`, `raw_spec` y `deeplink`.
- **AC-008 (Integraciones):** Los campos `source_file` y `spec_ref` DEBEN tener índices de tipo `keyword` creados de forma idempotente al asegurar la colección; todo campo de payload usado como criterio de filtro DEBE tener su índice correspondiente.
- **AC-009 (Reglas de negocio):** La decisión de omitir o indexar una fuente DEBE tomarse una sola vez por fuente, antes de procesar su primera operación, y DEBE mantenerse constante durante toda la ejecución.
- **AC-010 (Casos de uso):** La CLI DEBE soportar las opciones: `--source portal|files`, `--specs-dir`, `--list-only`, `--dry-run`, `--recreate`, `--force` y `--no-enrich`.
- **AC-011 (Reglas de negocio):** Las operaciones de recreación de la colección o borrado masivo SOLO DEBEN ejecutarse tras confirmación explícita del operador.
- **AC-012 (Casos de uso):** `--recreate` DEBE recrear la colección y DEBE continuar con la ingesta en la misma ejecución; NO DEBE terminar con la colección vacía.
- **AC-013 (Reglas de negocio):** La idempotencia DEBE funcionar así: sin `--force`, omitir las fuentes ya indexadas; con `--force`, borrar los puntos previos de esa fuente antes de reindexar; con `--dry-run`, ejecutar toda la preparación sin escribir ningún punto.
- **AC-014 (Salidas del sistema):** El sistema DEBE mostrar progreso operación a operación y DEBE forzar codificación UTF-8 en la salida estándar de Windows.
- **AC-015 (Casos de uso):** Con `--source files`, el sistema DEBE leer recursivamente los archivos `.json`, `.yaml` y `.yml` del directorio indicado por `LOCAL_SPECS_DIR` o por `--specs-dir`.
- **AC-016 (Procesamiento de datos):** En modo archivos, el `source_file` DEBE ser `file:{ruta_relativa}` respecto del directorio de specs, y el deeplink DEBE quedar vacío.
- **AC-017 (Procesamiento de datos):** El directorio de specs y las rutas de archivos descubiertas DEBEN resolverse ambos a forma absoluta antes de calcular la ruta relativa; el `source_file` resultante DEBE ser idéntico independientemente de si la configuración usa ruta relativa o absoluta.
- **AC-018 (Integraciones):** El modo archivos NO DEBE exigir `IBM_PORTAL_HOST` ni credenciales IAM.
- **AC-019 (Procesamiento de datos):** El sistema DEBE tolerar BOM al inicio de los archivos OpenAPI locales.
- **AC-020 (Idoneidad funcional):** Tras la lectura de archivos locales, el pipeline de extracción, enriquecimiento e indexación DEBE ser idéntico al del modo portal.
- **AC-021 (Fiabilidad):** DEBE existir una prueba que inspeccione el punto realmente enviado a la escritura y afirme la presencia simultánea de los dos vectores nombrados.
- **AC-022 (Fiabilidad):** DEBE existir una prueba que afirme el tipo del objeto entregado en la rama dispersa, tanto al indexar como al consultar.
- **AC-023 (Fiabilidad):** DEBE existir una prueba con varias operaciones de la misma fuente que verifique que todas se indexan; una prueba con una sola operación por fuente no es suficiente.
- **AC-024 (Fiabilidad):** Antes de dar por terminada la ingesta, DEBE verificarse que el número de puntos en la colección es coherente con el número de operaciones extraídas.
- **AC-025 (Integraciones):** El proveedor de embeddings DEBE ser configurable mediante `EMBED_PROVIDER=openai|watsonx` leído desde la capa de configuración; el valor por defecto es `openai`.
- **AC-026 (Procesamiento de datos):** Cuando `EMBED_PROVIDER=openai`, el sistema DEBE usar el modelo `text-embedding-3-large` truncado a 1024 dimensiones (`EMBED_DIM=1024`). Cuando `EMBED_PROVIDER=watsonx`, DEBE usar `ibm/granite-embedding-278m-multilingual` con 768 dimensiones (`EMBED_DIM=768`).
- **AC-027 (Reglas de negocio):** `EMBED_DIM` DEBE declararse una sola vez en `.env` y NUNCA DEBE aparecer como literal en el código; cambiar `EMBED_DIM` o cambiar de proveedor invalida la colección y obliga a reindexar.

---

## Complejidad sugerida

- **Story points:** 8
- **Justificación:** Engloba el pipeline completo de ingesta (enriquecimiento LLM, embeddings, escritura híbrida, idempotencia, modos portal y archivos) con requisitos críticos de verificabilidad derivados de fallos reales. Mayor complejidad y riesgo que cualquier otra US del proyecto.

## Repositorios

- smart-api-search-ibm-hackaton

## Validación

### INVEST

| Letra | Criterio      | Resultado | Notas |
| ----- | ------------- | --------- | ----- |
| **I** | Independiente | Parcial   | Presupone que existe una colección Qdrant y que las operaciones fueron extraídas (US-002); la ingesta portal también depende de US-001. Sin embargo, el pipeline de enriquecimiento e indexación puede implementarse y probarse de forma independiente con specs de prueba locales. |
| **N** | Negociable    | Cumple    | El número de palabras del texto LLM, el formato de la cabecera indexable y las opciones de CLI son ajustables. |
| **V** | Valiosa       | Cumple    | Sin esta historia no existe base vectorial que buscar; es el núcleo funcional del sistema. |
| **E** | Estimable     | Cumple    | Los requisitos son muy detallados; la implementación previa (con sus fallos documentados) da una referencia sólida de complejidad. |
| **S** | Parcial       | Parcial   | La historia es grande por combinar F-04 y F-07 según la instrucción del usuario. Podría dividirse, pero se mantiene unida por decisión explícita. |
| **T** | Testeable     | Cumple    | Todos los criterios son verificables; los AC-021–AC-024 son pruebas de verificabilidad explícitas derivadas de fallos reales. |

### Definition of Ready (DoR)

| Criterio DoR                       | Estado  | Notas |
| ---------------------------------- | ------- | ----- |
| Dependencias listas                | Cumple  | Qdrant Cloud disponible; credenciales en `.env`; operaciones extraídas (US-002). |
| Inputs/outputs claros              | Cumple  | Entradas: operaciones extraídas + credenciales de LLM/embeddings. Salidas: colección Qdrant con puntos híbridos y progreso en consola. |
| Repositorios definidos             | Cumple  | smart-api-search-ibm-hackaton |
| Sin decisiones técnicas pendientes | Cumple  | Pipeline, idempotencia, modo archivos y reglas de verificabilidad están completamente especificados. |
| Referencias de UI                  | No aplica | Proceso de línea de comandos. |
| Sin aclaraciones pendientes        | Cumple  | La combinación F-04 + F-07 en una sola US es instrucción explícita del usuario. |

## Observaciones

- La dimensión **S** es `Parcial` porque F-04 y F-07 se unieron en esta US por instrucción explícita del usuario. Si en el futuro se necesita paralelizar el trabajo, pueden dividirse en US-003a y US-003b con los IDs actuales reservados.
- La dependencia de US-001 (modo portal) y US-002 (extracción) afecta la dimensión **I** a `Parcial`, pero el pipeline de indexación es implementable y testeable de forma autónoma con archivos locales.
