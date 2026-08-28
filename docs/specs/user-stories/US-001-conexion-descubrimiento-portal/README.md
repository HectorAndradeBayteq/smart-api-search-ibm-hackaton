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
  Casos de prueba: [TC-001](./test-cases/TC-001-autenticacion-iam-token-happy.md) · [TC-002](./test-cases/TC-002-autenticacion-iam-credenciales-invalidas-error.md)
- **AC-002 (Integraciones):** Si `IBM_PORTAL_AUTH=false`, el sistema NO DEBE solicitar token ni enviar cabecera `Authorization`; las variables IAM PUEDEN estar vacías o ausentes.
  Casos de prueba: [TC-003](./test-cases/TC-003-sin-autenticacion-happy.md)
- **AC-003 (Integraciones):** Si `IBM_PORTAL_VERIFY_SSL=false`, el sistema DEBE desactivar la verificación SSL y DEBE silenciar los avisos de certificado no confiable.
  Casos de prueba: [TC-004](./test-cases/TC-004-ssl-verificacion-desactivada-happy.md) · [TC-005](./test-cases/TC-005-ssl-verificacion-activa-error.md)
- **AC-004 (Integraciones):** El sistema DEBE listar APIs con paginación `GET /apis?page=N` y DEBE continuar hasta cubrir el total indicado por el campo `count` de la respuesta.
  Casos de prueba: [TC-006](./test-cases/TC-006-paginacion-listado-apis-happy.md) · [TC-007](./test-cases/TC-007-paginacion-count-cero-limite.md)
- **AC-005 (Integraciones):** El sistema DEBE obtener el detalle `GET /apis/{id}` en paralelo con un máximo de 12 peticiones en vuelo simultáneo, conservando el orden; el fallo de un detalle NO DEBE abortar el descubrimiento del resto.
  Casos de prueba: [TC-008](./test-cases/TC-008-descarga-paralela-detalle-apis-happy.md) · [TC-009](./test-cases/TC-009-descarga-paralela-fallo-parcial-error.md) · [TC-010](./test-cases/TC-010-descarga-paralela-limite-exacto-concurrencia.md)
- **AC-006 (Procesamiento de datos):** El sistema DEBE asignar a cada fuente un `source_name` estable con formato `portal:{slug}`; ante slugs duplicados DEBE añadir un sufijo numérico para que sean únicos.
  Casos de prueba: [TC-011](./test-cases/TC-011-source-name-slug-unico-happy.md) · [TC-012](./test-cases/TC-012-source-name-slug-duplicado-sufijo.md)
- **AC-007 (Procesamiento de datos):** El sistema DEBE construir un mapa de deeplink `(path, MÉTODO) → URL`; si no existe recurso para un par, el valor DEBE ser cadena vacía.
  Casos de prueba: [TC-013](./test-cases/TC-013-mapa-deeplinks-par-existente-happy.md) · [TC-014](./test-cases/TC-014-mapa-deeplinks-par-inexistente-cadena-vacia.md)
- **AC-008 (Integraciones):** El sistema DEBE descargar el attachment OpenAPI completo en formato JSON o YAML, tolerando BOM al inicio; NO DEBE reconstruir el spec desde `resources[]`.
  Casos de prueba: [TC-015](./test-cases/TC-015-descarga-attachment-json-bom-happy.md) · [TC-016](./test-cases/TC-016-descarga-attachment-yaml-bom-happy.md) · [TC-017](./test-cases/TC-017-descarga-attachment-sin-openapi-error.md)
- **AC-009 (Casos de uso):** El sistema DEBE fallar con un mensaje claro y sin traza técnica si falta `IBM_PORTAL_HOST`, si falta `IBM_API_KEY` con autenticación activa, o si una API no tiene attachment OpenAPI.
  Casos de prueba: [TC-018](./test-cases/TC-018-error-portal-host-ausente.md) · [TC-019](./test-cases/TC-019-error-ibm-key-ausente-con-auth.md) · [TC-020](./test-cases/TC-020-error-api-sin-attachment-mensaje-claro.md)
- **AC-010 (Fiabilidad):** La configuración del portal DEBE ser opcional en tiempo de carga. Ninguna variable del portal DEBE impedir arrancar el sistema en modo archivos ni ejecutar la suite de pruebas.
  Casos de prueba: [TC-021](./test-cases/TC-021-arranque-sin-variables-portal-modo-archivos.md) · [TC-022](./test-cases/TC-022-suite-pruebas-sin-variables-portal.md)

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
