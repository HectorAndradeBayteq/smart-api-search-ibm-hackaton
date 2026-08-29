# /work-plan realiza la planificación respectiva para docs\specs\user-stories\US-001-conexion-descubrimiento-portal

---

**Status:** active  **Date:** 2026-08-28

---

### 👤 User

---
name: work-plan
description: "Planifica trabajo de distintos tipos sin generar código ni pruebas. Dos tipos de plan: (1) tareas técnicas (TK-XXX) bajo una historia de usuario existente; (2) tareas de mantenimiento (WI-XXX) sin historia asociada — bugs, refactor, deuda técnica, actualización de dependencias, tareas operativas. Activar siempre que el usuario pida planificar implementación, descomponer trabajo, definir alcance técnico, documentar especificaciones técnicas o planificar mantenimiento / deuda técnica / refactor, aunque no nombre «tarea», «TK» o «WI». Activar también — por defecto — cuando solo entregue una referencia a una historia (p. ej. «US-004», «planifica US-007», «tareas para esta historia»): proponer stubs agrupados por repositorio que cubran los criterios de aceptacion (AC-XXX). Selecciona el tipo según haya o no historia asociada y carga su definición desde references/. Cuenta el trabajo archivado en docs/specs/archive/ al asignar IDs y detectar solapamientos; lo archivado no se edita."
license: MIT
---

# Skill: Planificar trabajo

Guía general para **planificar trabajo** produciendo documentos de especificación —no código ni pruebas— de **distintos tipos**. Cada tipo de plan tiene su propia definición (flujos, plantillas, validaciones) en `references/`. El cuerpo de este `SKILL.md` contiene únicamente lo **transversal** a todos los tipos; el detalle de cada tipo se carga solo cuando se necesita.

> **Qué no hace este skill (cualquier tipo):** no implementa código, no ejecuta pruebas, no crea ADRs. Lo que no está acordado va a **Observaciones** o se pregunta al usuario — nunca se inventa.

---

## Regla de handoff (transversal)

Todo paso a otra fase del ciclo se realiza **invocando el skill correspondiente**, nunca ejecutando ese trabajo directamente desde este skill. El ciclo es `work-define` → `work-plan` → `work-implement` → `work-integrate` (con `pr-create` como alternativa de cierre).

- **Si el usuario pide implementar** (escribir código, crear/ejecutar pruebas, "impleméntalo", "hazlo", "desarróllalo") mientras se está en `work-plan`: **invocar `/work-implement`** pasándole el contexto del artefacto. Este skill **no** escribe código ni ejecuta pruebas bajo ninguna circunstancia.
- **Solo se implementa trabajo en `Estado: Ready`.** Si el artefacto sigue en `Draft` (stub o incompleto), no hacer handoff a implementación: completarlo primero en este skill.
- **Si el conflicto es funcional** (contradice el `README.md` de una US), escalar a **`work-define`**; este skill no modifica la US.
- **Si una TK/WI menciona elementos técnicos sin especificación** (un modelo, API o flujo citado que no existe en `docs/specs/technical-docs/`) y el usuario pide más detalle sobre alguno de ellos, **delegar mediante subagente a `/design-define`**: ese skill hace el grilling técnico, crea/actualiza el documento de la capability y devuelve las referencias (ruta + ancla) para agregarlas a la sección **Referencias** de la TK/WI. Este skill **no** crea ni edita documentos en `technical-docs/`.

No sustituir una invocación de skill por "hacer el trabajo aquí". El handoff es explícito y por skill en cada frontera del ciclo.

---

## Subagente

**Si el proyecto define el subagente `docs-specialist`, ejecutar este skill bajo ese subagente**, sea cual sea el tipo de plan. Si no existe, ejecutar el flujo normalmente.

---

## Cómo preguntar al usuario

Cuando este skill (o cualquiera de sus referencias) indique **preguntar, pedir, confirmar, validar o sugerir** algo al usuario, hacerlo mediante la **herramienta de preguntas estructuradas** del cliente (la que renderiza opciones tappables o un selector) en lugar de redactar la pregunta como prosa libre. Reglas:

- **Opciones cortas y mutuamente excluyentes** (2–4 por pregunta) cuando la respuesta admita categorías; usar entrada libre solo si no hay forma razonable de enumerar opciones (p. ej. el objetivo breve de un stub).
- **No repreguntar** lo que ya está respondido en el contexto, en `.agents/MEMORY.md`, o en los documentos existentes del repo.
- **Recopilación inicial:** agrupar las preguntas pendientes en una sola tanda (hasta tres por bloque); no ir descubriendo huecos turno a turno.
- **Confirmaciones de creación:** una pregunta por turno con opciones claras (p. ej. Opciones: [Confirmar] / [Ajustar] / [Cancelar]); no crear archivos antes de la confirmación.
- **Fallback:** si el cliente no expone esta herramienta, formular la pregunta en prosa con opciones enumeradas (1, 2, 3…).

Cada vez que una referencia diga *preguntar al usuario*, *validar con el usuario*, *confirmar* o *sugerir al usuario* asume este mecanismo; no se repite allí.

---

## Resolución de idioma

El idioma de los documentos generados y de los mensajes al usuario se decide en este orden; detenerse en el primer paso que aplique:

1. **`.agents/MEMORY.md`** (raíz del repo) → línea `preferred language: <ISO 639-1>` (p. ej. `es`, `en`). Es la clave canónica que escribe `arch-init`; si existe, manda.
2. Si no, la preferencia de idioma del usuario que conste en el contexto de la sesión.
3. Si no, usar el idioma del mensaje del usuario y **preguntar si desea persistirlo** en `.agents/MEMORY.md` con `preferred language: <código>`.
4. Si no se puede inferir, **preguntar al usuario** qué idioma prefiere y, tras su respuesta, **preguntar si desea persistirlo** en `.agents/MEMORY.md`; no decidir el idioma por cuenta propia.

---

## Selección del tipo de plan

**Antes de cualquier otra cosa**, identificar qué tipo de plan corresponde y cargar su definición. No mezclar tipos en una misma ejecución.

La señal que distingue los tipos es **si el trabajo tiene una historia de usuario asociada o no**.

| Tipo de plan | Cómo se identifica | Definición a leer |
|--------------|--------------------|-------------------|
| **Tarea técnica de historia de usuario** | El trabajo **referencia una historia de usuario**: prefijo de historia `US-XXX` (p. ej. «planifica US-007», «tareas para esta historia»), una historia ubicada bajo el árbol de user-stories del repo, o la edición de una `TK-XXX` que cuelga de una US. | `references/user-story-tasks.md` — **leer antes de redactar.** |
| **Tarea de mantenimiento** | El trabajo **no tiene una historia de usuario asociada** (corrección de bug, refactor, deuda técnica, actualización de dependencias, tarea operativa), o el usuario pide explícitamente «plan/tarea de mantenimiento». | `references/maintenance-tasks.md` — **leer antes de redactar.** |

Reglas de selección:

- **Hay historia asociada → tarea de historia de usuario. No la hay → mantenimiento.** Leer la referencia correspondiente y seguir **únicamente** su flujo.
- **Una US archivada sigue siendo una US.** Antes de concluir que «no hay historia asociada», buscarla también bajo `docs/specs/archive/user-stories/`: `work-integrate` y `pr-create` mueven ahí la carpeta al cerrar el trabajo. Si aparece ahí, el tipo **es** tarea de historia de usuario y su referencia dirá que hay que parar por estar archivada — degradarla a `WI-XXX` por no encontrarla en la ruta activa crearía un artefacto nuevo para trabajo que ya existe. Ver [`work-integrate/references/archive.md`](../work-integrate/references/archive.md#contrato-para-el-resto-del-catálogo).
- Si no está claro **si existe o no** una historia asociada (p. ej. una referencia ambigua que podría apuntar a una US), **preguntar al usuario** antes de continuar; no asumir la existencia de una US ni inventarla.
- Si el tipo seleccionado aún no tiene su flujo definido, la propia referencia indica cómo proceder (p. ej. confirmar con el usuario en lugar de inventar estructura).

---

## Integración con un sistema de seguimiento externo (condicional)

La sincronización con un sistema de seguimiento de trabajo externo (Azure DevOps, Jira u otro) es transversal a los tipos de plan que crean work items, pero **solo aplica si el repositorio está vinculado a uno**. Este skill solo resuelve **si** hay vinculación y **qué** referencia cargar; todo el detalle propio de cada sistema (herramienta MCP, campos, tipos de work item, configuración de conexión, límites de formato) vive exclusivamente en su archivo de `references/` — nunca aquí ni en las referencias de tipo de plan.

1. **Detectar** la vinculación leyendo `.agents/MEMORY.md` (raíz del repo): buscar la señal `work_item_tracking: <sistema>` con valor no vacío (p. ej. `azure_devops`).
2. **Si NO hay señal** → el repo no usa un tracker externo. Continuar con el flujo del tipo de plan usando ID secuencial local; **no** leer ninguna referencia de tracker.
3. **Si hay señal** → cargar `references/<sistema>.md` (p. ej. `references/azure-devops.md` para `work_item_tracking: azure_devops`) y seguir **únicamente** sus pasos antes de crear cualquier archivo local. Si no existe un archivo de referencia para el sistema indicado, informar al usuario y continuar con ID secuencial local.

**Regla de fidelidad (transversal a cualquier sistema):** toda la información del documento local debe quedar representada en el work item externo — en un campo dedicado si el sistema lo expone (p. ej. un campo de criterios de aceptación), o dentro de la descripción si no lo expone. Ninguna sección del `.md` puede omitirse al sincronizar; el objetivo es poder reconstruir el documento completo a partir del work item si el archivo local se perdiera. Qué campo usa cada sistema para qué sección es detalle de su archivo de referencia.

---

## Mensaje al usuario

Solo resultados y lo que el usuario debe saber o decidir. No incluir razonamiento interno, cadenas de pensamiento ni narración del trabajo en curso («leí la US», «creé el archivo»). Si hay pendientes o aclaraciones, listarlos en viñetas agrupadas por artefacto.

---

## Mapa de referencias

| Archivo | Cuándo leerlo |
|---------|---------------|
| `references/user-story-tasks.md` | Tipo de plan = tarea técnica de historia de usuario. Contiene modos de invocación, ubicaciones, flujos (stub, TK completa, actualizar, sugerir stubs desde US), checklist, ejemplos y anti-patrones. |
| `references/maintenance-tasks.md` | Tipo de plan = tarea de mantenimiento. |
| `references/<sistema>.md` (p. ej. `azure-devops.md`) | Solo si se detecta vinculación a un tracker externo (ver [Integración con un sistema de seguimiento externo](#integración-con-un-sistema-de-seguimiento-externo-condicional)); el archivo concreto depende del valor de `work_item_tracking`. |
| `assets/task-template.md` | Plantilla canónica de una tarea de historia de usuario (`TK-XXX`). Leer antes de redactar el documento. |
| `assets/work-item-template.md` | Plantilla canónica de una tarea de mantenimiento (`WI-XXX`). Leer antes de redactar el documento. |


realiza la planificación respectiva para docs\specs\user-stories\US-001-conexion-descubrimiento-portal

---

### 🤖 Assistant

> 🔧 called: use_skill



> 🔧 **use_skill** — work-plan

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file, read_file

Now let me load the required reference files and the US in parallel:

> 🔧 **read_file** — .agents/MEMORY.md

> 🔧 **read_file** — .agents/skills/work-plan/references/user-story-tasks.md

> 🔧 **read_file** — .agents/skills/work-plan/assets/task-template.md

> 🔧 **read_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/README.md

### 🤖 Assistant

> 🔧 called: glob, execute_command, glob

Now let me check for existing TKs in the US folder and the current git branch:

> 🔧 **glob** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-*.md

> 🔧 **execute_command** — git branch --show-current

> 🔧 **glob** — docs/specs/archive/user-stories/US-001*/**

### 🤖 Assistant

> 🔧 called: ask_followup_question, update_todo_list

Good. No existing TKs, no archived US, current branch is `main` (not an implementation branch). The US is `Estado: Ready` with `AC-001`–`AC-010` defined. This is **Modo B — Sugerir stubs desde una US**.

Based on my analysis of the US:
- **Repositorio único:** `smart-api-search-ibm-hackaton`
- **AC categorías:** Integraciones (AC-001–AC-005, AC-008), Procesamiento de datos (AC-006, AC-007), Casos de uso (AC-009), Fiabilidad (AC-010)

Aquí está la propuesta de stubs ordenada por prioridad (infraestructura compartida → sin dependencias → con dependencias):

---

**Propuesta de stubs para US-001** (repositorio: `smart-api-search-ibm-hackaton`)

| # | TK tentativo | Archivo | Objetivo breve | AC cubiertos |
|---|-------------|---------|----------------|--------------|
| 1 | TK-001 | `TK-001-configuracion-cliente-portal.md` | Implementar el cliente HTTP del portal: configuración de variables de entorno (`IBM_PORTAL_HOST`, IAM), construcción del cliente httpx con control de SSL y opcionalidad en tiempo de carga | AC-002, AC-003, AC-010 |
| 2 | TK-002 | `TK-002-autenticacion-iam.md` | Implementar la obtención y adjunto del token IAM con `POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token` y cabecera `Authorization: bearer <token>` cuando `IBM_PORTAL_AUTH=true` | AC-001 |
| 3 | TK-003 | `TK-003-descubrimiento-paginado-apis.md` | Implementar el listado paginado de APIs con `GET /apis?page=N` hasta cubrir el total indicado por `count`, y la descarga de detalles `GET /apis/{id}` en paralelo con semáforo de 12 peticiones en vuelo | AC-004, AC-005 |
| 4 | TK-004 | `TK-004-procesamiento-fuente-deeplinks.md` | Implementar la asignación de `source_name` estable (`portal:{slug}` con sufijo numérico ante duplicados) y construcción del mapa de deeplinks `(path, MÉTODO) → URL` | AC-006, AC-007 |
| 5 | TK-005 | `TK-005-descarga-spec-openapi.md` | Implementar la descarga del attachment OpenAPI completo (JSON/YAML, tolerando BOM) sin reconstruir el spec desde `resources[]` | AC-008 |
| 6 | TK-006 | `TK-006-manejo-errores-validacion.md` | Implementar mensajes de error claros (sin traza técnica) ante ausencia de `IBM_PORTAL_HOST`, `IBM_API_KEY` con auth activa, o API sin attachment OpenAPI | AC-009 |

**Orden de priorización:**
- **TK-001** — infraestructura compartida: el cliente del portal y la configuración base son la base de todo lo demás
- **TK-002** — sin dependencias sobre otras TK (solo usa el cliente de TK-001)
- **TK-003, TK-004, TK-005** — sin dependencias entre sí; pueden ejecutarse en paralelo (todas dependen de TK-001/TK-002)
- **TK-006** — con dependencias sobre TK-001–TK-005 (cubre errores a través de todo el flujo)

> ⚠️ No se han creado archivos todavía.

### 🤖 Assistant

¿Confirmas la propuesta de 6 stubs para US-001?

> 🔧 **ask_followup_question** — ¿Confirmas la propuesta de 6 stubs para US-001?

> 🔧 **update_todo_list** — 
[-] Proponer stubs consolidados en 3 TK para US-001
[ ] Confirmar propuesta con el usuario
[ ] Crear los 3 stubs confirmados


### 🤖 Assistant

> 🔧 called: ask_followup_question, update_todo_list

Propuesta consolidada a **3 TK** para `smart-api-search-ibm-hackaton`:

| # | TK tentativo | Archivo | Objetivo breve | AC cubiertos |
|---|-------------|---------|----------------|--------------|
| 1 | TK-001 | `TK-001-cliente-portal-autenticacion.md` | Implementar el cliente HTTP del portal: configuración de variables de entorno, obtención del token IAM cuando `IBM_PORTAL_AUTH=true`, desactivación SSL con `IBM_PORTAL_VERIFY_SSL=false`, y opcionalidad en tiempo de carga (no bloquear arranque en modo archivos) | AC-001, AC-002, AC-003, AC-010 |
| 2 | TK-002 | `TK-002-descubrimiento-y-descarga-specs.md` | Implementar el listado paginado de APIs (`GET /apis?page=N`), descarga paralela de detalles con semáforo de 12 peticiones, descarga del attachment OpenAPI completo (JSON/YAML, tolerando BOM) y manejo de errores parciales sin abortar el descubrimiento | AC-004, AC-005, AC-008 |
| 3 | TK-003 | `TK-003-procesamiento-fuente-errores.md` | Implementar la asignación de `source_name` estable (`portal:{slug}` con sufijo ante duplicados), construcción del mapa de deeplinks `(path, MÉTODO) → URL`, y mensajes de error claros sin traza técnica ante configuración inválida o API sin spec | AC-006, AC-007, AC-009 |

**Orden:** TK-001 (infraestructura compartida: cliente base) → TK-002 y TK-003 (sin dependencias entre sí, dependen de TK-001).

> ⚠️ No se han creado archivos todavía.

### 🤖 Assistant

¿Confirmas la propuesta consolidada en 3 TK para US-001?

> 🔧 **ask_followup_question** — ¿Confirmas la propuesta consolidada en 3 TK para US-001?

> 🔧 **update_todo_list** — [x] Proponer stubs consolidados en 3 TK para US-001
[-] Crear los 3 archivos stub TK-001, TK-002, TK-003
[ ] Reportar stubs creados con cobertura AC

### 🤖 Assistant

> 🔧 called: write_file, write_file, write_file, update_todo_list

Creo los 3 stubs:

> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md

> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-001-cliente-portal-autenticacion.md

> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-003-procesamiento-fuente-errores.md

> 🔧 **update_todo_list** — [x] Proponer stubs consolidados en 3 TK para US-001
[x] Crear los 3 archivos stub TK-001, TK-002, TK-003


### 🤖 Assistant

Stubs creados en `docs/specs/user-stories/US-001-conexion-descubrimiento-portal/`:

| Archivo | AC cubiertos |
|---------|-------------|
| [`TK-001-cliente-portal-autenticacion.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-001-cliente-portal-autenticacion.md) | AC-001, AC-002, AC-003, AC-010 |
| [`TK-002-descubrimiento-y-descarga-specs.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md) | AC-004, AC-005, AC-008 |
| [`TK-003-procesamiento-fuente-errores.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-003-procesamiento-fuente-errores.md) | AC-006, AC-007, AC-009 |

Los tres están en `Estado: Draft`. Para elevar cada TK a `Ready` (y habilitar `/work-implement`) hay que completar el **Plan de implementación** detallado en cada una. Puedes pedirlo tarea por tarea con `work-plan` en modo A.

---

### 👤 User

---
name: work-plan
description: "Planifica trabajo de distintos tipos sin generar código ni pruebas. Dos tipos de plan: (1) tareas técnicas (TK-XXX) bajo una historia de usuario existente; (2) tareas de mantenimiento (WI-XXX) sin historia asociada — bugs, refactor, deuda técnica, actualización de dependencias, tareas operativas. Activar siempre que el usuario pida planificar implementación, descomponer trabajo, definir alcance técnico, documentar especificaciones técnicas o planificar mantenimiento / deuda técnica / refactor, aunque no nombre «tarea», «TK» o «WI». Activar también — por defecto — cuando solo entregue una referencia a una historia (p. ej. «US-004», «planifica US-007», «tareas para esta historia»): proponer stubs agrupados por repositorio que cubran los criterios de aceptacion (AC-XXX). Selecciona el tipo según haya o no historia asociada y carga su definición desde references/. Cuenta el trabajo archivado en docs/specs/archive/ al asignar IDs y detectar solapamientos; lo archivado no se edita."
license: MIT
---

# Skill: Planificar trabajo

Guía general para **planificar trabajo** produciendo documentos de especificación —no código ni pruebas— de **distintos tipos**. Cada tipo de plan tiene su propia definición (flujos, plantillas, validaciones) en `references/`. El cuerpo de este `SKILL.md` contiene únicamente lo **transversal** a todos los tipos; el detalle de cada tipo se carga solo cuando se necesita.

> **Qué no hace este skill (cualquier tipo):** no implementa código, no ejecuta pruebas, no crea ADRs. Lo que no está acordado va a **Observaciones** o se pregunta al usuario — nunca se inventa.

---

## Regla de handoff (transversal)

Todo paso a otra fase del ciclo se realiza **invocando el skill correspondiente**, nunca ejecutando ese trabajo directamente desde este skill. El ciclo es `work-define` → `work-plan` → `work-implement` → `work-integrate` (con `pr-create` como alternativa de cierre).

- **Si el usuario pide implementar** (escribir código, crear/ejecutar pruebas, "impleméntalo", "hazlo", "desarróllalo") mientras se está en `work-plan`: **invocar `/work-implement`** pasándole el contexto del artefacto. Este skill **no** escribe código ni ejecuta pruebas bajo ninguna circunstancia.
- **Solo se implementa trabajo en `Estado: Ready`.** Si el artefacto sigue en `Draft` (stub o incompleto), no hacer handoff a implementación: completarlo primero en este skill.
- **Si el conflicto es funcional** (contradice el `README.md` de una US), escalar a **`work-define`**; este skill no modifica la US.
- **Si una TK/WI menciona elementos técnicos sin especificación** (un modelo, API o flujo citado que no existe en `docs/specs/technical-docs/`) y el usuario pide más detalle sobre alguno de ellos, **delegar mediante subagente a `/design-define`**: ese skill hace el grilling técnico, crea/actualiza el documento de la capability y devuelve las referencias (ruta + ancla) para agregarlas a la sección **Referencias** de la TK/WI. Este skill **no** crea ni edita documentos en `technical-docs/`.

No sustituir una invocación de skill por "hacer el trabajo aquí". El handoff es explícito y por skill en cada frontera del ciclo.

---

## Subagente

**Si el proyecto define el subagente `docs-specialist`, ejecutar este skill bajo ese subagente**, sea cual sea el tipo de plan. Si no existe, ejecutar el flujo normalmente.

---

## Cómo preguntar al usuario

Cuando este skill (o cualquiera de sus referencias) indique **preguntar, pedir, confirmar, validar o sugerir** algo al usuario, hacerlo mediante la **herramienta de preguntas estructuradas** del cliente (la que renderiza opciones tappables o un selector) en lugar de redactar la pregunta como prosa libre. Reglas:

- **Opciones cortas y mutuamente excluyentes** (2–4 por pregunta) cuando la respuesta admita categorías; usar entrada libre solo si no hay forma razonable de enumerar opciones (p. ej. el objetivo breve de un stub).
- **No repreguntar** lo que ya está respondido en el contexto, en `.agents/MEMORY.md`, o en los documentos existentes del repo.
- **Recopilación inicial:** agrupar las preguntas pendientes en una sola tanda (hasta tres por bloque); no ir descubriendo huecos turno a turno.
- **Confirmaciones de creación:** una pregunta por turno con opciones claras (p. ej. Opciones: [Confirmar] / [Ajustar] / [Cancelar]); no crear archivos antes de la confirmación.
- **Fallback:** si el cliente no expone esta herramienta, formular la pregunta en prosa con opciones enumeradas (1, 2, 3…).

Cada vez que una referencia diga *preguntar al usuario*, *validar con el usuario*, *confirmar* o *sugerir al usuario* asume este mecanismo; no se repite allí.

---

## Resolución de idioma

El idioma de los documentos generados y de los mensajes al usuario se decide en este orden; detenerse en el primer paso que aplique:

1. **`.agents/MEMORY.md`** (raíz del repo) → línea `preferred language: <ISO 639-1>` (p. ej. `es`, `en`). Es la clave canónica que escribe `arch-init`; si existe, manda.
2. Si no, la preferencia de idioma del usuario que conste en el contexto de la sesión.
3. Si no, usar el idioma del mensaje del usuario y **preguntar si desea persistirlo** en `.agents/MEMORY.md` con `preferred language: <código>`.
4. Si no se puede inferir, **preguntar al usuario** qué idioma prefiere y, tras su respuesta, **preguntar si desea persistirlo** en `.agents/MEMORY.md`; no decidir el idioma por cuenta propia.

---

## Selección del tipo de plan

**Antes de cualquier otra cosa**, identificar qué tipo de plan corresponde y cargar su definición. No mezclar tipos en una misma ejecución.

La señal que distingue los tipos es **si el trabajo tiene una historia de usuario asociada o no**.

| Tipo de plan | Cómo se identifica | Definición a leer |
|--------------|--------------------|-------------------|
| **Tarea técnica de historia de usuario** | El trabajo **referencia una historia de usuario**: prefijo de historia `US-XXX` (p. ej. «planifica US-007», «tareas para esta historia»), una historia ubicada bajo el árbol de user-stories del repo, o la edición de una `TK-XXX` que cuelga de una US. | `references/user-story-tasks.md` — **leer antes de redactar.** |
| **Tarea de mantenimiento** | El trabajo **no tiene una historia de usuario asociada** (corrección de bug, refactor, deuda técnica, actualización de dependencias, tarea operativa), o el usuario pide explícitamente «plan/tarea de mantenimiento». | `references/maintenance-tasks.md` — **leer antes de redactar.** |

Reglas de selección:

- **Hay historia asociada → tarea de historia de usuario. No la hay → mantenimiento.** Leer la referencia correspondiente y seguir **únicamente** su flujo.
- **Una US archivada sigue siendo una US.** Antes de concluir que «no hay historia asociada», buscarla también bajo `docs/specs/archive/user-stories/`: `work-integrate` y `pr-create` mueven ahí la carpeta al cerrar el trabajo. Si aparece ahí, el tipo **es** tarea de historia de usuario y su referencia dirá que hay que parar por estar archivada — degradarla a `WI-XXX` por no encontrarla en la ruta activa crearía un artefacto nuevo para trabajo que ya existe. Ver [`work-integrate/references/archive.md`](../work-integrate/references/archive.md#contrato-para-el-resto-del-catálogo).
- Si no está claro **si existe o no** una historia asociada (p. ej. una referencia ambigua que podría apuntar a una US), **preguntar al usuario** antes de continuar; no asumir la existencia de una US ni inventarla.
- Si el tipo seleccionado aún no tiene su flujo definido, la propia referencia indica cómo proceder (p. ej. confirmar con el usuario en lugar de inventar estructura).

---

## Integración con un sistema de seguimiento externo (condicional)

La sincronización con un sistema de seguimiento de trabajo externo (Azure DevOps, Jira u otro) es transversal a los tipos de plan que crean work items, pero **solo aplica si el repositorio está vinculado a uno**. Este skill solo resuelve **si** hay vinculación y **qué** referencia cargar; todo el detalle propio de cada sistema (herramienta MCP, campos, tipos de work item, configuración de conexión, límites de formato) vive exclusivamente en su archivo de `references/` — nunca aquí ni en las referencias de tipo de plan.

1. **Detectar** la vinculación leyendo `.agents/MEMORY.md` (raíz del repo): buscar la señal `work_item_tracking: <sistema>` con valor no vacío (p. ej. `azure_devops`).
2. **Si NO hay señal** → el repo no usa un tracker externo. Continuar con el flujo del tipo de plan usando ID secuencial local; **no** leer ninguna referencia de tracker.
3. **Si hay señal** → cargar `references/<sistema>.md` (p. ej. `references/azure-devops.md` para `work_item_tracking: azure_devops`) y seguir **únicamente** sus pasos antes de crear cualquier archivo local. Si no existe un archivo de referencia para el sistema indicado, informar al usuario y continuar con ID secuencial local.

**Regla de fidelidad (transversal a cualquier sistema):** toda la información del documento local debe quedar representada en el work item externo — en un campo dedicado si el sistema lo expone (p. ej. un campo de criterios de aceptación), o dentro de la descripción si no lo expone. Ninguna sección del `.md` puede omitirse al sincronizar; el objetivo es poder reconstruir el documento completo a partir del work item si el archivo local se perdiera. Qué campo usa cada sistema para qué sección es detalle de su archivo de referencia.

---

## Mensaje al usuario

Solo resultados y lo que el usuario debe saber o decidir. No incluir razonamiento interno, cadenas de pensamiento ni narración del trabajo en curso («leí la US», «creé el archivo»). Si hay pendientes o aclaraciones, listarlos en viñetas agrupadas por artefacto.

---

## Mapa de referencias

| Archivo | Cuándo leerlo |
|---------|---------------|
| `references/user-story-tasks.md` | Tipo de plan = tarea técnica de historia de usuario. Contiene modos de invocación, ubicaciones, flujos (stub, TK completa, actualizar, sugerir stubs desde US), checklist, ejemplos y anti-patrones. |
| `references/maintenance-tasks.md` | Tipo de plan = tarea de mantenimiento. |
| `references/<sistema>.md` (p. ej. `azure-devops.md`) | Solo si se detecta vinculación a un tracker externo (ver [Integración con un sistema de seguimiento externo](#integración-con-un-sistema-de-seguimiento-externo-condicional)); el archivo concreto depende del valor de `work_item_tracking`. |
| `assets/task-template.md` | Plantilla canónica de una tarea de historia de usuario (`TK-XXX`). Leer antes de redactar el documento. |
| `assets/work-item-template.md` | Plantilla canónica de una tarea de mantenimiento (`WI-XXX`). Leer antes de redactar el documento. |


completar TK

---

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md

### 🤖 Assistant

> 🔧 called: list_files, list_files, read_file, GetSymbolsOverview, read_file, read_file, read_file

Now let me explore the codebase to understand the existing structure before writing the plan:

> 🔧 **list_files** — src/smart_api_search

> 🔧 **list_files** — docs/specs

> 🔧 **read_file** — docs/specs/technical-docs/smart-api-search.md

> 🔧 **GetSymbolsOverview** — src/smart_api_search/config.py

> 🔧 **read_file** — src/smart_api_search/config.py

> 🔧 **read_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-001-cliente-portal-autenticacion.md

> 🔧 **read_file** — src/smart_api_search/cli/ingest.py

### 🤖 Assistant

> 🔧 called: list_files, list_files, read_file, update_todo_list

Now let me check for existing ADRs and tests to understand the project conventions:

> 🔧 **list_files** — docs/adr

> 🔧 **list_files** — tests

> 🔧 **read_file** — pyproject.toml

> 🔧 **update_todo_list** — [-] Completar TK-002 a Estado: Ready


### 🤖 Assistant

> 🔧 called: write_file, update_todo_list

Tengo todo lo necesario. TK-002 cubre AC-004 (paginación), AC-005 (paralelismo + resiliencia) y AC-008 (descarga de attachment). La dependencia de TK-001 ya está documentada y el repositorio único es `smart-api-search-ibm-hackaton`. El flujo FL-01 del technical-doc es la referencia canónica. Redacto la TK completa:

> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md

> 🔧 **update_todo_list** — [x] Completar TK-002 a Estado: Ready


### 🤖 Assistant

[`TK-002-descubrimiento-y-descarga-specs.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md) elevada a **`Estado: Ready`**.

**Resumen de cambios:**

- **Descripción** — ampliada con el módulo destino (`cli/ingest.py`) y las restricciones concretas (orden conservado, fallo no fatal por detalle)
- **Dependencias** — `TK-001` (cliente configurado), `httpx`, `asyncio.Semaphore`
- **Referencias** — ancla `#fl-01` al technical-doc (pasos 3 y tabla de errores del paso 3)
- **Archivos afectados** — `cli/ingest.py` (modificado), `tests/test_portal_discovery.py` (nuevo)
- **Plan (IT-01 → IT-06):**
  - IT-01: paginación con `while` sobre `count`
  - IT-02: descarga paralela con `asyncio.Semaphore(12)`, resultado `None` en fallos parciales
  - IT-03: descarga del attachment; detección `json`/`yaml` por extensión o `Content-Type`
  - IT-04: eliminación de BOM en bytes y texto; prohibición de reconstruir desde `resources[]`
  - IT-05: integración en el flujo principal con respeto a `--dry-run`
  - IT-06: pruebas unitarias con mocks de `httpx.AsyncClient`

**Observaciones pendientes** (no bloquean `Ready`): timeout/reintentos sin fijar en la spec técnica; estructura exacta del campo `attachment` por confirmar contra el portal real.

Para implementar, invocar `/work-implement` sobre esta TK (requiere que TK-001 esté también en `Ready`).

---

### 👤 User

---
name: work-plan
description: "Planifica trabajo de distintos tipos sin generar código ni pruebas. Dos tipos de plan: (1) tareas técnicas (TK-XXX) bajo una historia de usuario existente; (2) tareas de mantenimiento (WI-XXX) sin historia asociada — bugs, refactor, deuda técnica, actualización de dependencias, tareas operativas. Activar siempre que el usuario pida planificar implementación, descomponer trabajo, definir alcance técnico, documentar especificaciones técnicas o planificar mantenimiento / deuda técnica / refactor, aunque no nombre «tarea», «TK» o «WI». Activar también — por defecto — cuando solo entregue una referencia a una historia (p. ej. «US-004», «planifica US-007», «tareas para esta historia»): proponer stubs agrupados por repositorio que cubran los criterios de aceptacion (AC-XXX). Selecciona el tipo según haya o no historia asociada y carga su definición desde references/. Cuenta el trabajo archivado en docs/specs/archive/ al asignar IDs y detectar solapamientos; lo archivado no se edita."
license: MIT
---

# Skill: Planificar trabajo

Guía general para **planificar trabajo** produciendo documentos de especificación —no código ni pruebas— de **distintos tipos**. Cada tipo de plan tiene su propia definición (flujos, plantillas, validaciones) en `references/`. El cuerpo de este `SKILL.md` contiene únicamente lo **transversal** a todos los tipos; el detalle de cada tipo se carga solo cuando se necesita.

> **Qué no hace este skill (cualquier tipo):** no implementa código, no ejecuta pruebas, no crea ADRs. Lo que no está acordado va a **Observaciones** o se pregunta al usuario — nunca se inventa.

---

## Regla de handoff (transversal)

Todo paso a otra fase del ciclo se realiza **invocando el skill correspondiente**, nunca ejecutando ese trabajo directamente desde este skill. El ciclo es `work-define` → `work-plan` → `work-implement` → `work-integrate` (con `pr-create` como alternativa de cierre).

- **Si el usuario pide implementar** (escribir código, crear/ejecutar pruebas, "impleméntalo", "hazlo", "desarróllalo") mientras se está en `work-plan`: **invocar `/work-implement`** pasándole el contexto del artefacto. Este skill **no** escribe código ni ejecuta pruebas bajo ninguna circunstancia.
- **Solo se implementa trabajo en `Estado: Ready`.** Si el artefacto sigue en `Draft` (stub o incompleto), no hacer handoff a implementación: completarlo primero en este skill.
- **Si el conflicto es funcional** (contradice el `README.md` de una US), escalar a **`work-define`**; este skill no modifica la US.
- **Si una TK/WI menciona elementos técnicos sin especificación** (un modelo, API o flujo citado que no existe en `docs/specs/technical-docs/`) y el usuario pide más detalle sobre alguno de ellos, **delegar mediante subagente a `/design-define`**: ese skill hace el grilling técnico, crea/actualiza el documento de la capability y devuelve las referencias (ruta + ancla) para agregarlas a la sección **Referencias** de la TK/WI. Este skill **no** crea ni edita documentos en `technical-docs/`.

No sustituir una invocación de skill por "hacer el trabajo aquí". El handoff es explícito y por skill en cada frontera del ciclo.

---

## Subagente

**Si el proyecto define el subagente `docs-specialist`, ejecutar este skill bajo ese subagente**, sea cual sea el tipo de plan. Si no existe, ejecutar el flujo normalmente.

---

## Cómo preguntar al usuario

Cuando este skill (o cualquiera de sus referencias) indique **preguntar, pedir, confirmar, validar o sugerir** algo al usuario, hacerlo mediante la **herramienta de preguntas estructuradas** del cliente (la que renderiza opciones tappables o un selector) en lugar de redactar la pregunta como prosa libre. Reglas:

- **Opciones cortas y mutuamente excluyentes** (2–4 por pregunta) cuando la respuesta admita categorías; usar entrada libre solo si no hay forma razonable de enumerar opciones (p. ej. el objetivo breve de un stub).
- **No repreguntar** lo que ya está respondido en el contexto, en `.agents/MEMORY.md`, o en los documentos existentes del repo.
- **Recopilación inicial:** agrupar las preguntas pendientes en una sola tanda (hasta tres por bloque); no ir descubriendo huecos turno a turno.
- **Confirmaciones de creación:** una pregunta por turno con opciones claras (p. ej. Opciones: [Confirmar] / [Ajustar] / [Cancelar]); no crear archivos antes de la confirmación.
- **Fallback:** si el cliente no expone esta herramienta, formular la pregunta en prosa con opciones enumeradas (1, 2, 3…).

Cada vez que una referencia diga *preguntar al usuario*, *validar con el usuario*, *confirmar* o *sugerir al usuario* asume este mecanismo; no se repite allí.

---

## Resolución de idioma

El idioma de los documentos generados y de los mensajes al usuario se decide en este orden; detenerse en el primer paso que aplique:

1. **`.agents/MEMORY.md`** (raíz del repo) → línea `preferred language: <ISO 639-1>` (p. ej. `es`, `en`). Es la clave canónica que escribe `arch-init`; si existe, manda.
2. Si no, la preferencia de idioma del usuario que conste en el contexto de la sesión.
3. Si no, usar el idioma del mensaje del usuario y **preguntar si desea persistirlo** en `.agents/MEMORY.md` con `preferred language: <código>`.
4. Si no se puede inferir, **preguntar al usuario** qué idioma prefiere y, tras su respuesta, **preguntar si desea persistirlo** en `.agents/MEMORY.md`; no decidir el idioma por cuenta propia.

---

## Selección del tipo de plan

**Antes de cualquier otra cosa**, identificar qué tipo de plan corresponde y cargar su definición. No mezclar tipos en una misma ejecución.

La señal que distingue los tipos es **si el trabajo tiene una historia de usuario asociada o no**.

| Tipo de plan | Cómo se identifica | Definición a leer |
|--------------|--------------------|-------------------|
| **Tarea técnica de historia de usuario** | El trabajo **referencia una historia de usuario**: prefijo de historia `US-XXX` (p. ej. «planifica US-007», «tareas para esta historia»), una historia ubicada bajo el árbol de user-stories del repo, o la edición de una `TK-XXX` que cuelga de una US. | `references/user-story-tasks.md` — **leer antes de redactar.** |
| **Tarea de mantenimiento** | El trabajo **no tiene una historia de usuario asociada** (corrección de bug, refactor, deuda técnica, actualización de dependencias, tarea operativa), o el usuario pide explícitamente «plan/tarea de mantenimiento». | `references/maintenance-tasks.md` — **leer antes de redactar.** |

Reglas de selección:

- **Hay historia asociada → tarea de historia de usuario. No la hay → mantenimiento.** Leer la referencia correspondiente y seguir **únicamente** su flujo.
- **Una US archivada sigue siendo una US.** Antes de concluir que «no hay historia asociada», buscarla también bajo `docs/specs/archive/user-stories/`: `work-integrate` y `pr-create` mueven ahí la carpeta al cerrar el trabajo. Si aparece ahí, el tipo **es** tarea de historia de usuario y su referencia dirá que hay que parar por estar archivada — degradarla a `WI-XXX` por no encontrarla en la ruta activa crearía un artefacto nuevo para trabajo que ya existe. Ver [`work-integrate/references/archive.md`](../work-integrate/references/archive.md#contrato-para-el-resto-del-catálogo).
- Si no está claro **si existe o no** una historia asociada (p. ej. una referencia ambigua que podría apuntar a una US), **preguntar al usuario** antes de continuar; no asumir la existencia de una US ni inventarla.
- Si el tipo seleccionado aún no tiene su flujo definido, la propia referencia indica cómo proceder (p. ej. confirmar con el usuario en lugar de inventar estructura).

---

## Integración con un sistema de seguimiento externo (condicional)

La sincronización con un sistema de seguimiento de trabajo externo (Azure DevOps, Jira u otro) es transversal a los tipos de plan que crean work items, pero **solo aplica si el repositorio está vinculado a uno**. Este skill solo resuelve **si** hay vinculación y **qué** referencia cargar; todo el detalle propio de cada sistema (herramienta MCP, campos, tipos de work item, configuración de conexión, límites de formato) vive exclusivamente en su archivo de `references/` — nunca aquí ni en las referencias de tipo de plan.

1. **Detectar** la vinculación leyendo `.agents/MEMORY.md` (raíz del repo): buscar la señal `work_item_tracking: <sistema>` con valor no vacío (p. ej. `azure_devops`).
2. **Si NO hay señal** → el repo no usa un tracker externo. Continuar con el flujo del tipo de plan usando ID secuencial local; **no** leer ninguna referencia de tracker.
3. **Si hay señal** → cargar `references/<sistema>.md` (p. ej. `references/azure-devops.md` para `work_item_tracking: azure_devops`) y seguir **únicamente** sus pasos antes de crear cualquier archivo local. Si no existe un archivo de referencia para el sistema indicado, informar al usuario y continuar con ID secuencial local.

**Regla de fidelidad (transversal a cualquier sistema):** toda la información del documento local debe quedar representada en el work item externo — en un campo dedicado si el sistema lo expone (p. ej. un campo de criterios de aceptación), o dentro de la descripción si no lo expone. Ninguna sección del `.md` puede omitirse al sincronizar; el objetivo es poder reconstruir el documento completo a partir del work item si el archivo local se perdiera. Qué campo usa cada sistema para qué sección es detalle de su archivo de referencia.

---

## Mensaje al usuario

Solo resultados y lo que el usuario debe saber o decidir. No incluir razonamiento interno, cadenas de pensamiento ni narración del trabajo en curso («leí la US», «creé el archivo»). Si hay pendientes o aclaraciones, listarlos en viñetas agrupadas por artefacto.

---

## Mapa de referencias

| Archivo | Cuándo leerlo |
|---------|---------------|
| `references/user-story-tasks.md` | Tipo de plan = tarea técnica de historia de usuario. Contiene modos de invocación, ubicaciones, flujos (stub, TK completa, actualizar, sugerir stubs desde US), checklist, ejemplos y anti-patrones. |
| `references/maintenance-tasks.md` | Tipo de plan = tarea de mantenimiento. |
| `references/<sistema>.md` (p. ej. `azure-devops.md`) | Solo si se detecta vinculación a un tracker externo (ver [Integración con un sistema de seguimiento externo](#integración-con-un-sistema-de-seguimiento-externo-condicional)); el archivo concreto depende del valor de `work_item_tracking`. |
| `assets/task-template.md` | Plantilla canónica de una tarea de historia de usuario (`TK-XXX`). Leer antes de redactar el documento. |
| `assets/work-item-template.md` | Plantilla canónica de una tarea de mantenimiento (`WI-XXX`). Leer antes de redactar el documento. |


completa las demas tareas tk1 y tk3

---

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-003-procesamiento-fuente-errores.md

### 🤖 Assistant

> 🔧 called: update_todo_list, write_file, write_file, update_todo_list

Tengo todos los contextos necesarios del turno anterior. Completo ambas TK en paralelo:

> 🔧 **update_todo_list** — [-] Completar TK-001 a Estado: Ready
[-] Completar TK-003 a Estado: Ready


> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-001-cliente-portal-autenticacion.md

> 🔧 **write_file** — docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-003-procesamiento-fuente-errores.md

> 🔧 **update_todo_list** — [x] Completar TK-001 a Estado: Ready
[x] Completar TK-003 a Estado: Ready


### 🤖 Assistant

Las tres TK de US-001 están ahora en **`Estado: Ready`**:

| Tarea | Estado | Plan |
|-------|--------|------|
| [`TK-001-cliente-portal-autenticacion.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-001-cliente-portal-autenticacion.md) | ✅ Ready | IT-01…IT-05 (Settings opcionales, `get_iam_token`, `build_portal_client`, opcionalidad en carga, tests) |
| [`TK-002-descubrimiento-y-descarga-specs.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-002-descubrimiento-y-descarga-specs.md) | ✅ Ready | IT-01…IT-06 (paginación, paralelo semáforo, attachment, BOM, integración, tests) |
| [`TK-003-procesamiento-fuente-errores.md`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/TK-003-procesamiento-fuente-errores.md) | ✅ Ready | IT-01…IT-06 (source_name + sufijos, mapa deeplinks, validaciones config, propagación de errores, integración, tests) |

**Orden de implementación:** TK-001 → TK-002 y TK-003 (paralelo entre sí, ambas dependen de TK-001).

Para comenzar la implementación, invocar `/work-implement` indicando la TK a trabajar.