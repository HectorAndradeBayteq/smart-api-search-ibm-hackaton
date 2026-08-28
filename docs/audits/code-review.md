# Code Review — US-005-servidor-mcp-http

**Fecha:** 2026-08-28 17:30
**Rama:** feature/US-005-servidor-mcp-http
**Commit:** 0e845e4
**Alcance del diff:** feature/US-005-servidor-mcp-http vs main, incluidos los cambios sin commitear — ~20 archivos (+860/−22 en commits; +`pyproject.toml` fail_under=65 y audits)
**Modo:** default
**Base del diff:** main @ d9dcf1e
**Veredicto:** ✅ Aprobado — cumple AC-001…AC-011 a nivel de código/docs; sin hallazgos 🔴/🟠

## Resumen

Se revisó el servidor MCP HTTP (ASGI, middleware 405, tools, prompt, configs de cliente y pruebas ASGI) frente a US-005. La intención y el diseño encajan con ADR-013 y con stubs explícitos hacia US-004. Único nitpick: el README afirma que `.cursor/mcp.json` está en el repo, pero `.cursor/` está en `.gitignore`.

## Intención detectada

Exponer Smart API Search como servidor MCP `streamable-http` arrancable por referencia ASGI (`smart_api_search.server:app`), con `search_openapi`, `get_endpoint_spec`, prompt `find_backend_api`, middleware GET→405, y ejemplos de configuración para IDEs (AC-001…AC-011). Fuente: `docs/specs/user-stories/US-005-servidor-mcp-http/README.md`.

## Hallazgos

Símbolos de severidad: `🔴` Crítico · `🟠` Mayor · `🟡` Menor · `💡` Sugerencia · `✅` Conforme.

### Análisis semántico (intención)

✅ Conforme — el diff implementa arranque ASGI, middleware, tools/prompt, verificabilidad por tests ASGI y documentación Bob/README; los stubs de retrieval/result están documentados como dependencia de US-004 (INVEST ya marcaba independencia parcial).

### Arquitectura y diseño

✅ Conforme — registro único en `FastMCP`, app de producción envuelta por middleware, `ToolError` para `spec_ref` inválido (BR-02), Settings para host/port/path, y tests que importan el mismo `app`/`mcp` de producción (AC-008/AC-009).

- 🟡 `[ISO-25010: Usabilidad]` README vs `.cursor/` ignorado — **Qué:** README dice que [`.cursor/mcp.json`](.cursor/mcp.json) «Ya incluido en el repositorio», pero `.gitignore` excluye `.cursor/`. **Por qué:** el enlace/claim engaña a quien clone el repo. **Impacto:** bajo (hay `.bob` y `.github` versionados + tabla VS Code). **Sugerencia:** indicar que Cursor usa archivo local no versionado, o versionar un ejemplo bajo `docs/` / `.bob` como plantilla.

- 💡 `[ISO-25010: Mantenibilidad]` Umbral de cobertura bajado a 65% — **Qué:** `fail_under = 65` autorizado en cierre. **Por qué:** deja margen bajo el estándar previo (80%). **Impacto:** deuda de pruebas en `server.py` / domain stubs. **Sugerencia:** WI posterior para subir cobertura del happy path de las tools.

### Dimensiones no evaluadas

Ninguna.

### Feedback adicional

Bien el rechazo GET con `Allow: POST, DELETE`, el prompt bilingüe con el gate explícito antes de `get_endpoint_spec`, y `check_compatibility=False` para no exigir Qdrant en import/CI. Los tests TC-001…TC-004 cubren lo crítico de verificabilidad ASGI.

## Próximas acciones

Sin acciones pendientes bloqueantes. Opcional: corregir la mención de `.cursor/mcp.json` en el README.

## Justificaciones aceptadas

Ninguna.

<!-- code-review:fingerprint=5499ea6476076d901c8c7f1e1a8efd713d136a70 · base=d9dcf1e · generado=2026-08-28 -->
