# Casos de prueba — US-001: Conexión y descubrimiento de APIs en el Developer Portal

Índice de casos de prueba generados a partir de los criterios de aceptación AC-001–AC-010 de la historia de usuario [US-001](../README.md).

| TC | Perspectiva | Tipo de prueba | Estado | Prioridad | Criterio de aceptación |
|----|-------------|----------------|--------|-----------|------------------------|
| [TC-001](./TC-001-autenticacion-iam-token-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-001 |
| [TC-002](./TC-002-autenticacion-iam-credenciales-invalidas-error.md) | Error | Unit, Integration | Ready | Alta | AC-001 |
| [TC-003](./TC-003-sin-autenticacion-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-002 |
| [TC-004](./TC-004-ssl-verificacion-desactivada-happy.md) | Happy Path | Unit, Integration | Ready | Media | AC-003 |
| [TC-005](./TC-005-ssl-verificacion-activa-error.md) | Error | Unit, Integration | Ready | Media | AC-003 |
| [TC-006](./TC-006-paginacion-listado-apis-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-004 |
| [TC-007](./TC-007-paginacion-count-cero-limite.md) | Límite | Unit | Ready | Media | AC-004 |
| [TC-008](./TC-008-descarga-paralela-detalle-apis-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-005 |
| [TC-009](./TC-009-descarga-paralela-fallo-parcial-error.md) | Error | Unit, Integration | Ready | Alta | AC-005 |
| [TC-010](./TC-010-descarga-paralela-limite-exacto-concurrencia.md) | Límite | Unit | Ready | Media | AC-005 |
| [TC-011](./TC-011-source-name-slug-unico-happy.md) | Happy Path | Unit | Ready | Alta | AC-006 |
| [TC-012](./TC-012-source-name-slug-duplicado-sufijo.md) | Error | Unit | Ready | Alta | AC-006 |
| [TC-013](./TC-013-mapa-deeplinks-par-existente-happy.md) | Happy Path | Unit | Ready | Alta | AC-007 |
| [TC-014](./TC-014-mapa-deeplinks-par-inexistente-cadena-vacia.md) | Error | Unit | Ready | Alta | AC-007 |
| [TC-015](./TC-015-descarga-attachment-json-bom-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-008 |
| [TC-016](./TC-016-descarga-attachment-yaml-bom-happy.md) | Happy Path | Unit, Integration | Ready | Alta | AC-008 |
| [TC-017](./TC-017-descarga-attachment-sin-openapi-error.md) | Error | Unit, Integration | Ready | Alta | AC-008 |
| [TC-018](./TC-018-error-portal-host-ausente.md) | Error | Unit | Ready | Alta | AC-009 |
| [TC-019](./TC-019-error-ibm-key-ausente-con-auth.md) | Error | Unit | Ready | Alta | AC-009 |
| [TC-020](./TC-020-error-api-sin-attachment-mensaje-claro.md) | Error | Unit, Integration | Ready | Alta | AC-009 |
| [TC-021](./TC-021-arranque-sin-variables-portal-modo-archivos.md) | Happy Path | Unit, Integration | Ready | Alta | AC-010 |
| [TC-022](./TC-022-suite-pruebas-sin-variables-portal.md) | Happy Path | Unit, Integration | Ready | Alta | AC-010 |
