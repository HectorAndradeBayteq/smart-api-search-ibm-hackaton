# Test Cases — US-005: Servidor MCP HTTP

Índice de casos de prueba para US-005. Los TC automatizados cubren criterios críticos (ASGI, middleware, ToolError, registro de tools/prompt). El resto son **Manual** por alcance autorizado (solo automatizar AC críticos).

| TC | Perspectiva | Tipo de prueba | Estado | Prioridad | Criterio de aceptación |
|----|-------------|----------------|--------|-----------|------------------------|
| [TC-001](./TC-001-asgi-init-no-reexporta-simbolos-happy.md) | Happy Path | Unit | Ready | Alta | AC-008 |
| [TC-002](./TC-002-asgi-app-registra-herramientas-y-prompt-happy.md) | Happy Path | Unit | Ready | Alta | AC-009 |
| [TC-003](./TC-003-middleware-get-405-happy.md) | Happy Path | Integration | Ready | Alta | AC-002 |
| [TC-004](./TC-004-get-endpoint-spec-ref-invalido-tool-error.md) | Error | Unit | Ready | Alta | AC-005 |
| [TC-005](./TC-005-arranque-defaults-stateless-manual.md) | Happy Path | Manual | Ready | Media | AC-001 |
| [TC-006](./TC-006-search-openapi-formato-manual.md) | Happy Path | Manual | Ready | Media | AC-003 |
| [TC-007](./TC-007-get-endpoint-spec-formato-manual.md) | Happy Path | Manual | Ready | Media | AC-004 |
| [TC-008](./TC-008-prompt-flujo-manual.md) | Happy Path | Manual | Ready | Media | AC-006 |
| [TC-009](./TC-009-instructions-servidor-manual.md) | Happy Path | Manual | Ready | Media | AC-007 |
| [TC-010](./TC-010-config-clientes-arranque-manual.md) | Happy Path | Manual | Ready | Media | AC-010 |
| [TC-011](./TC-011-readme-ibm-bob-manual.md) | Happy Path | Manual | Ready | Media | AC-011 |
