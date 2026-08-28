# US-001: Conexión y descubrimiento de APIs en el Developer Portal

**Estado:** Ready
**Fecha de creación:** 2025-07-19
**Última actualización:** 2025-07-19

## Descripción

**COMO** desarrollador que usa un IDE conectado al servidor MCP
**QUIERO** que el sistema se conecte al IBM API Connect Developer Portal con autenticación IAM opcional y descubra todas las APIs disponibles
**PARA** poder indexarlas y buscarlas en lenguaje natural sin tener que navegar el portal manualmente

## Contexto

El sistema tiene dos modos de autenticación frente al portal: con token IAM (`IBM_PORTAL_AUTH=true`) y sin autenticación (`IBM_PORTAL_AUTH=false`). La configuración del portal es opcional en tiempo de carga: ninguna variable del portal debe impedir arrancar el servidor ni ejecutar las pruebas cuando se opera en modo archivos.

## Fuera de alcance

- Gestión de usuarios o permisos en el portal.
- Sincronización automática o periódica con el portal (sin demanda del operador).
- Frontend propio para visualizar las APIs descubiertas.

## Referencias

- Ninguna por ahora

## Criterios de aceptación

- **AC-001 (Integraciones):** Si `IBM_PORTAL_AUTH=true`, el sistema DEBE obtener el token de acceso con `POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token` y cuerpo `{"apikey": ...}` y DEBE enviar la cabecera `Authorization: bearer <token>` en todas las llamadas al portal.
- **AC-002 (Integraciones):** Si `IBM_PORTAL_AUTH=false`, el sistema NO DEBE solicitar token ni enviar cabecera `Authorization`; las variables IAM PUEDEN estar vacías o ausentes.
- **AC-003 (Integraciones):** Si `IBM_PORTAL_VERIFY_SSL=false`, el sistema DEBE desactivar la verificación SSL y DEBE silenciar los avisos de certificado no confiable.
- **AC-004 (Integraciones):** El sistema DEBE listar APIs con paginación `GET /apis?page=N` y DEBE continuar hasta cubrir el total indicado por el campo `count` de la respuesta.
- **AC-005 (Integraciones):** El sistema DEBE obtener el detalle `GET /apis/{id}` en paralelo con un máximo de 12 peticiones en vuelo simultáneo, conservando el orden; el fallo de un detalle NO DEBE abortar el descubrimiento del resto.
- **AC-006 (Procesamiento de datos):** El sistema DEBE asignar a cada fuente un `source_name` estable con formato `portal:{slug}`; ante slugs duplicados DEBE añadir un sufijo numérico para que sean únicos.
- **AC-007 (Procesamiento de datos):** El sistema DEBE construir un mapa de deeplink `(path, MÉTODO) → URL`; si no existe recurso para un par, el valor DEBE ser cadena vacía.
- **AC-008 (Integraciones):** El sistema DEBE descargar el attachment OpenAPI completo en formato JSON o YAML, tolerando BOM al inicio; NO DEBE reconstruir el spec desde `resources[]`.
- **AC-009 (Casos de uso):** El sistema DEBE fallar con un mensaje claro y sin traza técnica si falta `IBM_PORTAL_HOST`, si falta `IBM_API_KEY` con autenticación activa, o si una API no tiene attachment OpenAPI.
- **AC-010 (Fiabilidad):** La configuración del portal DEBE ser opcional en tiempo de carga. Ninguna variable del portal DEBE impedir arrancar el sistema en modo archivos ni ejecutar la suite de pruebas.

---

## Complejidad sugerida

- **Story points:** 5
- **Justificación:** Implica autenticación IAM, paginación, paralelismo con límite de concurrencia, manejo de errores parciales y construcción del mapa de deeplinks. Riesgo moderado por variabilidad del portal real.

## Repositorios

- smart-api-search-ibm-hackaton

## Validación

### INVEST

| Letra | Criterio      | Resultado | Notas |
| ----- | ------------- | --------- | ----- |
| **I** | Independiente | Cumple    | No depende de otras US; es la capa de ingesta de portal que otras US pueden presuponer como dada. |
| **N** | Negociable    | Cumple    | El número de peticiones en paralelo (12) y los detalles del mapa de deeplink son ajustables. |
| **V** | Valiosa       | Cumple    | Sin esta historia el sistema no puede descubrir APIs del portal. |
| **E** | Estimable     | Cumple    | Los requisitos son concretos y la implementación previa da referencias de complejidad. |
| **S** | Pequeña       | Cumple    | Alcance acotado a la fase de conexión y descubrimiento; la extracción y la indexación son otras US. |
| **T** | Testeable     | Cumple    | Todos los criterios son verificables con mocks del portal; AC-010 requiere prueba de arranque en modo archivos. |

### Definition of Ready (DoR)

| Criterio DoR                       | Estado   | Notas |
| ---------------------------------- | -------- | ----- |
| Dependencias listas                | Cumple   | No depende de otras US. Requiere Qdrant Cloud y credenciales IAM disponibles en `.env` para pruebas de integración. |
| Inputs/outputs claros              | Cumple   | Entradas: variables de entorno del portal. Salidas: lista de fuentes con spec OpenAPI y mapa de deeplinks. |
| Repositorios definidos             | Cumple   | smart-api-search-ibm-hackaton |
| Sin decisiones técnicas pendientes | Cumple   | Autenticación, paginación, paralelismo y manejo de errores están especificados en AC-001–AC-010. |
| Referencias de UI                  | No aplica | No hay UI propia; es un proceso de línea de comandos. |
| Sin aclaraciones pendientes        | Cumple   | Ninguna. |

## Observaciones

- Ninguna.
