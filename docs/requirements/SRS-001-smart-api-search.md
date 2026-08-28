# SRS-001 — Smart API Search

| Campo | Valor |
| --- | --- |
| **ID** | SRS-001 |
| **Título** | Smart API Search — servidor MCP de búsqueda semántica sobre catálogos OpenAPI |
| **Versión** | 2.0 |
| **Estado** | Approved (alcance cerrado) |
| **Idioma del proyecto** | Español |
| **Base** | Consolida la v1.2 con las lecciones verificadas de una implementación completa previa |

---

## 1. Introducción

### 1.1 Propósito

Este documento especifica un sistema que indexa catálogos de APIs descritos en OpenAPI/Swagger en una
base vectorial híbrida y los expone a un IDE mediante el protocolo MCP, de modo que un desarrollador
pueda descubrir endpoints preguntando en lenguaje natural, sin leer documentación.

### 1.2 Nota sobre esta versión

La versión 2.0 no añade funcionalidad respecto de la 1.2. Incorpora los requisitos que faltaron en la
primera implementación y que solo se descubrieron al operar el sistema contra servicios reales. Todos
ellos están marcados con el símbolo **⚠** y desarrollados en el **anexo A**.

El patrón común de aquellos fallos fue el mismo: el sistema pasaba todas sus pruebas y cumplía todos
sus criterios de aceptación, pero no funcionaba. Los requisitos existían; lo que faltaba era una
verificación que los anclara al comportamiento real del sistema integrado. Por eso esta versión
incluye una sección de **requisitos de verificabilidad** (§5) que es tan obligatoria como las demás.

### 1.3 Alcance

**Dentro de alcance**

- Ingesta por línea de comandos desde un IBM API Connect Developer Portal, con autenticación IAM y
  también con acceso libre sin token.
- Ingesta por línea de comandos desde archivos OpenAPI/Swagger locales, con la misma unidad de
  indexación y el mismo pipeline posterior.
- Enriquecimiento semántico con LLM e indexación híbrida en Qdrant Cloud.
- Recuperación híbrida: expansión HyDE, rama densa, rama BM25 y fusión RRF.
- Servidor MCP por HTTP (`streamable-http`) con dos herramientas y un prompt.
- Metadatos opcionales de presentación por categoría.
- Compuerta de calidad local: tipado estricto, linter, pruebas, cobertura y contratos de arquitectura.

**Fuera de alcance**

- Frontend propio.
- Despliegue en nube, contenedores y CI/CD.
- Reutilización de colecciones vectoriales de otros sistemas; se usa una colección nueva y aislada.

### 1.4 Definiciones

| Término | Significado |
| --- | --- |
| **Operación** | Par `(path, método HTTP)` de un documento OpenAPI. Es la unidad de indexación. |
| **Fuente** (`source_file`) | Origen de un conjunto de operaciones. `portal:{slug}` o `file:{ruta_relativa}`. |
| **`spec_ref`** | Identificador de una operación: `source_file\|METHOD\|/path`. |
| **Punto** | Registro en la base vectorial: dos vectores nombrados más un payload. |
| **Enriquecimiento** | Descripción generada por LLM que se embebe en lugar del JSON crudo. |
| **HyDE** | Expansión de la consulta a una descripción hipotética de endpoint antes de embeberla. |
| **RRF** | Reciprocal Rank Fusion, el mecanismo que combina los rankings denso y BM25. |

---

## 2. Descripción general

### 2.1 Contexto

El sistema tiene dos procesos independientes que se comunican únicamente a través de la base
vectorial: un proceso de **ingesta** que se ejecuta bajo demanda desde la terminal, y un **servidor
MCP** de larga duración al que se conecta el IDE. No comparten estado en memoria.

### 2.2 Características

| ID | Característica | Prioridad |
| --- | --- | --- |
| F-01 | Conexión y descubrimiento en el Developer Portal | Must |
| F-02 | Extracción de endpoints desde OpenAPI/Swagger | Must |
| F-03 | Metadatos de presentación por categoría | Must |
| F-04 | Enriquecimiento LLM e indexación híbrida | Must |
| F-05 | Búsqueda híbrida con HyDE y RRF | Must |
| F-06 | Servidor MCP HTTP con dos tools y un prompt | Must |
| F-07 | Ingesta desde archivos locales | Must |

### 2.3 Restricciones técnicas

| Área | Decisión |
| --- | --- |
| Runtime | Python 3.12, pip, entorno virtual `.venv`, dependencias fijadas con `==` |
| Sistema operativo de desarrollo | Windows, scripts de arranque en PowerShell |
| Servidor MCP | FastMCP sobre transporte `streamable-http`, servido con uvicorn |
| Base vectorial | Qdrant Cloud, colección híbrida (denso + disperso BM25), fusión RRF |
| Proveedor de embeddings | Configurable: `EMBED_PROVIDER=openai` (por defecto) o `EMBED_PROVIDER=watsonx` — ver ADR-014 |
| Embeddings — OpenAI | `text-embedding-3-large` truncado a **1024** dimensiones (`EMBED_DIM=1024`) ⚠ |
| Embeddings — Watsonx | `ibm/granite-embedding-278m-multilingual`, **768** dimensiones, ventana 512 tokens (`EMBED_DIM=768`) |
| LLM generativo | OpenAI Responses API, para enriquecimiento y para HyDE |
| Configuración | Variables de entorno mediante archivo `.env` no versionado |

**⚠ Sobre la dimensión.** `EMBED_DIM` es un valor único y configurable, leído desde la capa de
configuración. Su valor depende del proveedor activo: **1024** para OpenAI, **768** para Watsonx.
En la implementación previa convivieron dos valores contradictorios (3072 y 1024) en distintos
documentos. Cambiar `EMBED_DIM` (o cambiar de proveedor) invalida la colección y obliga a reindexar;
por eso `EMBED_DIM` debe declararse **una sola vez** en `.env` y nunca aparecer literal en el código.

---

## 3. Requisitos funcionales

### 3.1 F-01 — Conexión y descubrimiento en el Developer Portal

| ID | Requisito |
| --- | --- |
| RF-01.1 | Si `IBM_PORTAL_AUTH=true`, obtener token con `POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token` y cuerpo `{"apikey": ...}`; usar cabecera `Authorization: bearer <token>`. |
| RF-01.2 | Si `IBM_PORTAL_AUTH=false`, no pedir token ni enviar `Authorization`; las variables IAM pueden estar vacías. |
| RF-01.3 | Si `IBM_PORTAL_VERIFY_SSL=false`, desactivar la verificación SSL y silenciar los avisos de certificado no confiable. |
| RF-01.4 | Listar APIs con paginación `GET /apis?page=N` hasta cubrir el total indicado por `count`. |
| RF-01.5 | Obtener el detalle `GET /apis/{id}` en paralelo, máximo 12 en vuelo, conservando el orden; el fallo de un detalle no aborta el resto. |
| RF-01.6 | Asignar `source_name` estable con formato `portal:{slug}`; ante slugs duplicados, añadir sufijo numérico. |
| RF-01.7 | Construir un mapa de deeplink `(path, MÉTODO) → URL`; si no hay recurso, cadena vacía. |
| RF-01.8 | Descargar el attachment OpenAPI completo (JSON o YAML, tolerando BOM); no reconstruir el spec desde `resources[]`. |
| RF-01.9 | Fallar con mensaje claro y sin traza técnica si falta `IBM_PORTAL_HOST`, si falta `IBM_API_KEY` con auth activa, o si una API no tiene attachment. |
| RF-01.10 ⚠ | La configuración del portal debe ser **opcional en tiempo de carga**. Solo se valida cuando se ejecuta la ingesta en modo portal. Ninguna variable del portal debe impedir arrancar el sistema en modo archivos ni ejecutar las pruebas. |

### 3.2 F-02 — Extracción de endpoints

| ID | Requisito |
| --- | --- |
| RF-02.1 | Recorrer `paths` y extraer los métodos HTTP estándar presentes (`get`, `post`, `put`, `delete`, `patch`, `head`, `options`, `trace`), normalizados a mayúsculas. |
| RF-02.2 | Soportar OpenAPI 3.x y Swagger 2.0; en Swagger 2.0 componer la URL base desde `schemes`, `host` y `basePath`. |
| RF-02.3 | Ante specs pobres, obtener texto útil con la cadena de respaldo: `summary` → primera línea de `description` → `operationId` → descripciones de parámetros. |
| RF-02.4 | Conservar por operación un fragmento crudo JSON (info del spec, servidor base, formato, path, method y el objeto operation) para la herramienta de consulta de spec. |
| RF-02.5 | Si un spec no declara `paths`, generar un documento marcador para que la API no desaparezca en silencio del índice. |
| RF-02.6 | Aplicar una función de limpieza de texto (macros, admoniciones, espacios redundantes) tanto al indexar como al presentar. |

### 3.3 F-03 — Metadatos de presentación por categoría

| ID | Requisito |
| --- | --- |
| RF-03.1 | Un archivo versionado bajo `config/` permite definir, opcionalmente y por categoría, un título y una descripción de presentación. |
| RF-03.2 | Si una categoría no define esos metadatos, usar el título y la descripción del propio spec. |
| RF-03.3 | Si el archivo no existe o tiene sintaxis inválida, el proceso falla al arrancar, antes de procesar ningún spec, indicando ruta y causa. |

### 3.4 F-04 — Enriquecimiento e indexación híbrida

| ID | Requisito |
| --- | --- |
| RF-04.1 | Colección híbrida: vector denso con métrica coseno y dimensión `EMBED_DIM`, más vector disperso BM25 con modificador IDF. |
| RF-04.2 | Enriquecer cada operación con LLM: 250–400 palabras en inglés, con propósito, capacidades, casos de uso, una línea `Keywords:` y una sección `Example questions users might ask:`. |
| RF-04.3 | Opción `--no-enrich` que indexa los metadatos del spec sin llamar al LLM. |
| RF-04.4 | Texto indexable = cabecera compacta `[categoría \| API \| formato \| método path \| tags \| base]` + texto enriquecido. El deeplink **no** forma parte del texto embebido. |
| RF-04.5 | Payload almacenado con, al menos: `api_title`, `api_version`, `api_description`, `category`, `method`, `path`, `summary`, `description`, `tags`, `operationId`, `environment`, `server_url`, `spec_format`, `source_file`, `enriched_text`, `raw_spec` y `deeplink`. |
| RF-04.6 | Idempotencia: omitir fuentes ya indexadas; `--force` borra los puntos previos de esa fuente antes de reindexar; `--dry-run` ejecuta toda la preparación sin escribir. |
| RF-04.7 | La CLI ofrece `--source portal\|files`, `--specs-dir`, `--list-only`, `--dry-run`, `--recreate`, `--force` y `--no-enrich`. |
| RF-04.8 | Recrear la colección o borrar datos masivamente solo tras confirmación explícita del operador. |
| RF-04.9 | Mostrar progreso operación a operación y forzar codificación UTF-8 en la salida estándar de Windows. |
| RF-04.10 ⚠ | **Cada punto escrito debe contener simultáneamente el vector denso y el vector disperso.** Una escritura con un solo vector deja el índice a medias sin producir error visible, y por tanto está prohibida. |
| RF-04.11 ⚠ | **La generación del vector disperso se delega al motor.** El texto se entrega envuelto en el objeto de documento que el motor exige para inferir el vector en el servidor, no como cadena simple. Esto aplica igual al indexar y al consultar. |
| RF-04.12 ⚠ | **Todo campo de payload usado como criterio de filtro debe tener un índice de tipo `keyword`**, creado de forma idempotente al asegurar la colección. Como mínimo `source_file` y `spec_ref`, porque los usan la idempotencia y la recuperación por referencia. |
| RF-04.13 ⚠ | **La decisión de omitir o indexar una fuente se toma una sola vez por fuente y antes de procesar su primera operación**, y permanece constante durante toda la ejecución. Reevaluarla por operación provoca que una fuente nueva se auto-omita tras indexar su primer punto. |
| RF-04.14 ⚠ | `--recreate` recrea la colección y **continúa** con la ingesta en la misma ejecución, informando al final cuántos puntos indexó. No debe terminar dejando la colección vacía. |

### 3.5 F-05 — Búsqueda híbrida

| ID | Requisito |
| --- | --- |
| RF-05.1 | Flujo: HyDE opcional → embeber el texto expandido → prefetch denso y prefetch BM25 en paralelo → fusión RRF → devolver `top_k` con 1 ≤ `top_k` ≤ 10. |
| RF-05.2 | HyDE debe poder desactivarse por configuración; desactivado, se embebe la consulta original y no se llama al LLM. |
| RF-05.3 | La rama BM25 recibe siempre el **contenido textual** de la consulta original, sin reescritura ni expansión. ⚠ Esta prohibición se refiere al texto, no a la envoltura técnica que exige RF-04.11. |
| RF-05.4 | Cada resultado incluye: ranking, categoría, method, path, summary, description, definición consolidada, URL de llamada, deeplink, `spec_ref`, tags, origen, params y body. |
| RF-05.5 | La URL de llamada es la URL base del spec más el path del endpoint; no es la URL del portal ni el deeplink. |
| RF-05.6 | Los params incluyen los declarados en la operación normalizados más los inferidos del template del path; se omiten los parámetros sin nombre. |
| RF-05.7 | `spec_ref` tiene formato `source_file\|METHOD\|/path` con parseo estricto de tres segmentos no vacíos. |
| RF-05.8 | La recuperación por referencia devuelve vacío sin lanzar excepción si el punto no existe. |
| RF-05.9 | Ingesta y recuperación usan exactamente el mismo modelo, dimensión y función de embedding, definidos en la capa compartida. |

### 3.6 F-06 — Servidor MCP

| ID | Requisito |
| --- | --- |
| RF-06.1 | Arrancar con uvicorn en `MCP_HOST`, `MCP_PORT` y `MCP_PATH` (por defecto `127.0.0.1`, `8000`, `/mcp`), en modo sin estado. |
| RF-06.2 | Un middleware intercepta `GET` al endpoint MCP y responde `405 Method Not Allowed` con cabecera `Allow: POST, DELETE`. |
| RF-06.3 | Tool `search_openapi(query, top_k=5)`: markdown compacto más contenido estructurado; no devuelve el JSON OpenAPI completo. |
| RF-06.4 | Tool `get_endpoint_spec(spec_ref)`: markdown más contenido estructurado con el fragmento OpenAPI, la URL de llamada y el deeplink; un `spec_ref` inválido o no encontrado se marca como error de herramienta, no como excepción. |
| RF-06.5 | Prompt `find_backend_api(need)`: guía el flujo buscar → presentar → pedir el spec solo si el usuario lo solicita explícitamente. |
| RF-06.6 | Las instrucciones del servidor indican: usar esta base de conocimiento para descubrir APIs, no buscar en el workspace, no traducir los nombres de categoría y no pegar JSON salvo petición explícita. |
| RF-06.7 | Entregar un ejemplo de configuración de cliente MCP (`type: http` y URL) usable en IBM Bob, VS Code, Cursor y GitHub Copilot, más un script `.ps1` de arranque que use el Python del entorno virtual. |
| RF-06.8 | Documentar en el README cómo registrar el servidor en IBM Bob. |
| RF-06.9 ⚠ | **El servidor se expone mediante la referencia ASGI del módulo, nunca ejecutando el módulo como `__main__`.** El paquete no debe reexportar símbolos que sombreen a sus propios submódulos. La combinación de ambas cosas provoca que se cargue el módulo dos veces y que se sirva una segunda instancia MCP **sin herramientas registradas**, con el cliente mostrando el servidor conectado pero vacío. |

### 3.7 F-07 — Ingesta desde archivos locales

| ID | Requisito |
| --- | --- |
| RF-07.1 | Con `--source files`, leer recursivamente los archivos `.json`, `.yaml` y `.yml` del directorio indicado por `LOCAL_SPECS_DIR` o por `--specs-dir`. |
| RF-07.2 | El `source_file` es `file:{ruta_relativa}` respecto del directorio de specs, y el deeplink queda vacío. |
| RF-07.3 | El modo archivos no exige `IBM_PORTAL_HOST` ni credenciales IAM. |
| RF-07.4 | Tras la lectura, el pipeline es idéntico al del modo portal: misma extracción, mismo enriquecimiento, misma indexación. |
| RF-07.5 ⚠ | **El directorio de specs y las rutas descubiertas se resuelven ambos a forma absoluta antes de calcular la ruta relativa.** Si la configuración aporta una ruta relativa y el descubrimiento devuelve rutas absolutas, relativizar una contra otra falla. El `source_file` resultante debe ser idéntico en ambos casos. |
| RF-07.6 | Tolerar BOM al inicio de los archivos. |

---

## 4. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-01 | El código de las capas de dominio debe pasar verificación de tipos en modo estricto. |
| RNF-02 | Todo el código debe pasar el linter y el verificador de formato sin diferencias. |
| RNF-03 | Cobertura de pruebas ≥ 80 % en las capas de dominio. ⚠ Ver RF-V.5 sobre el umbral por módulo. |
| RNF-04 | Las pruebas unitarias no realizan llamadas reales a servicios externos; toda integración se simula. |
| RNF-05 | Las pruebas que sí llaman a servicios externos se marcan y quedan excluidas de la ejecución por defecto. |
| RNF-06 | Ninguna credencial ni URL de servicio aparece literal en el código o en archivos versionados. |
| RNF-07 | Un contrato de arquitectura verificable impide que cualquier capa distinta de la compartida invoque directamente la API de embeddings. |
| RNF-08 | La latencia de búsqueda está dominada por las llamadas a los servicios externos, no por el servidor. |

---

## 5. Requisitos de verificabilidad ⚠

Esta sección es la principal lección de la primera implementación y es de cumplimiento obligatorio.

Todo requisito cuya violación es **silenciosa** —un vector que no se escribe, una instancia que no es
la que se sirve, un filtro que nunca encuentra nada, una fuente que se auto-omite— necesita una
verificación que lo observe desde fuera, recorriendo el mismo camino que la ejecución real. Un
requisito sin esa verificación se considera no implementado.

| ID | Requisito |
| --- | --- |
| RF-V.1 | Debe existir una prueba que inspeccione el punto realmente enviado a la escritura y afirme la presencia de los dos vectores nombrados (ancla RF-04.10). |
| RF-V.2 | Debe existir una prueba que afirme el tipo del objeto entregado en la rama dispersa, tanto al indexar como al consultar (ancla RF-04.11). |
| RF-V.3 | Debe existir una prueba con **varias operaciones de la misma fuente** que verifique que todas se indexan (ancla RF-04.13). Una prueba con una sola operación por fuente no detecta el fallo. |
| RF-V.4 | Debe existir una verificación sobre el **mismo objeto ASGI que sirve el entrypoint de producción** que afirme que expone las dos herramientas y el prompt (ancla RF-06.9). Importar la aplicación por un camino distinto al de producción no sirve: es exactamente el camino que no falla. |
| RF-V.5 | El umbral de cobertura agregado debe complementarse con un mínimo por módulo, o bien declararse explícitamente qué módulos quedan fuera y por qué. Un promedio alto puede ocultar módulos críticos con cobertura baja. |
| RF-V.6 | Toda prueba nacida de un fallo observado debe fallar si se revierte la corrección. Si pasa con y sin el fallo, no ancla nada. |
| RF-V.7 | Antes de dar por terminada la ingesta, verificar que el número de puntos en la colección es coherente con el número de operaciones extraídas, no solo que el proceso terminó sin error. |

---

## 6. Decisiones arquitectónicas a registrar

Insumo directo para la creación de los ADR. Las trece están validadas por la implementación previa.

| ID | Decisión | Dominio del estándar |
| --- | --- | --- |
| ADR-001 | FastMCP como framework del servidor MCP, con transporte `streamable-http` y uvicorn | api |
| ADR-002 | Qdrant Cloud como base vectorial con colección híbrida y fusión RRF | persistence |
| ADR-003 | Python 3.12, pip y entorno virtual como toolchain; scripts PowerShell | devops |
| ADR-004 | Compuerta de calidad: pruebas, cobertura, tipado estricto y linter | testing |
| ADR-005 | Unidad de indexación: la operación OpenAPI, no el archivo | retrieval |
| ADR-006 | Enriquecimiento con LLM en tiempo de ingesta, con modo rápido desactivable | retrieval |
| ADR-007 | Consulta híbrida con ramas densa y BM25 fusionadas con RRF | retrieval |
| ADR-008 | Expansión de consulta con HyDE, desactivable | retrieval |
| ADR-009 | Representación vectorial: modelo único truncado a `EMBED_DIM`, con fuente única en la capa compartida | retrieval |
| ADR-010 ⚠ | Inferencia de vectores dispersos delegada al motor: el cliente entrega texto envuelto en el objeto de documento del motor, al indexar y al consultar | retrieval |
| ADR-011 ⚠ | Los campos de payload usados como filtro forman parte del contrato de la colección y se indexan al asegurarla | persistence |
| ADR-012 ⚠ | Idempotencia de ingesta con granularidad de fuente, evaluada una sola vez y antes de escribir | retrieval |
| ADR-013 ⚠ | Arranque del servidor MCP por referencia ASGI, sin reexportar la aplicación en el paquete | api |

---

## Anexo A — Fallos verificados de la primera implementación

Los seis fallos que impidieron operar el sistema. Todos ocurrieron con la suite en verde.

**A-1. El vector disperso no se escribía.** La colección tenía esquema híbrido y la consulta buscaba
en ambas ramas, pero la escritura solo incluía el vector denso. La mitad BM25 del índice estaba vacía
en todos los puntos, sin ningún error visible. → RF-04.10, RF-V.1

**A-2. La rama dispersa de la consulta enviaba texto plano.** El motor respondió
`400 Bad Request: Expected some form of vector, id, or a type of query`. El requisito del estándar
decía que la consulta debía llegar «sin ninguna transformación», y esa redacción indujo el error. →
RF-04.11, RF-05.3, RF-V.2

**A-3. Los filtros por payload fallaban sin índice.** La ingesta abortaba con
`400 Bad Request: Index required but not found for "source_file" of one of the following types:
[keyword]`. Dos requisitos daban por hecho que se podía filtrar por esos campos; ninguno decía que
había que indexarlos primero. → RF-04.12

**A-4. La colección quedó con 6 puntos en vez de 272.** Uno por archivo. Al indexar la primera
operación de una fuente, la comprobación «¿ya está indexada?» pasaba a devolver verdadero para el
resto de operaciones de esa misma fuente. Las pruebas usaban una operación por fuente y nunca
ejercitaron el caso. → RF-04.13, RF-V.3, RF-V.7

**A-5. `--recreate` dejó la colección vacía.** Recreó y terminó sin indexar, sin avisar. Ningún
requisito definía si debía continuar. → RF-04.14

**A-6. El cliente MCP mostraba «Connected» con «No tools available».** El servidor arrancaba
ejecutando el módulo y el paquete reexportaba la aplicación; el módulo se cargaba dos veces y uvicorn
servía una segunda instancia sin herramientas. Las pruebas de integración pasaban porque importaban
la aplicación por el camino que no estaba roto. → RF-06.9, RF-V.4

---

## Anexo B — Deudas de proceso a no repetir

No son fallos de código, pero costaron tiempo en la primera pasada.

| Deuda | Cómo evitarla esta vez |
| --- | --- |
| Trabajo sin publicar: 27 commits en cinco ramas locales, ninguna en el remoto | Publicar la rama al cerrar cada historia |
| Estados desalineados: historias en `Ready` con su progreso en `Done` | Alinear el estado al cerrar cada unidad, no al final |
| Valor contradictorio de la dimensión del embedding en tres documentos | Declararlo una sola vez y referenciarlo desde el resto |
| Un ADR declaraba emitir un requisito de estándar que no existía | Verificar que cada requisito emitido existe en su estándar |
| Sin Definition of Done | Crearla al inicializar el proyecto, no al final |
