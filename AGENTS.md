# Agents

## Reglas operativas y arquitectónicas

- @.agents/MEMORY.md — memoria persistente del proyecto
- @docs/adr/README.md — índice de Architecture Decision Records (decisiones arquitectónicas vigentes)
- @docs/standards/README.md — índice de Estándares de Arquitectura

### Consideraciones

- Si la información es arquitectónica → consultar ADRs y/o Estándares
- Si es preferencia o regla operativa → usar MEMORY.md
- Si hay conflicto → prioridad: ADRs → Estándares → MEMORY.md

## Stack tecnológico

| Área | Detalle |
| ---- | ------- |
| **Runtime** | Python 3.12, pip, entorno virtual `.venv` |
| **Servidor MCP** | FastMCP ≥2.0 · transporte `streamable-http` · uvicorn ≥0.30 |
| **Base vectorial** | Qdrant Cloud · colección híbrida (denso + BM25) · fusión RRF |
| **Embeddings — OpenAI** | `text-embedding-3-large` · `EMBED_DIM=1024` (por defecto) |
| **Embeddings — Watsonx** | `ibm/granite-embedding-278m-multilingual` · 768 dims · 512 tokens · `EMBED_DIM=768` |
| **Proveedor activo** | Configurable: `EMBED_PROVIDER=openai\|watsonx` (`.env`) |
| **LLM generativo** | OpenAI Responses API (enriquecimiento + HyDE) |
| **Parseo OpenAPI** | pyyaml ≥6.0, httpx ≥0.27 |
| **Configuración** | `.env` (no versionado) · `python-dotenv` |
| **Scripts** | PowerShell (.ps1) · `start-server.ps1` |
| **Testing** | pytest ≥8.2 · pytest-cov · pytest-asyncio |
| **Tipado** | mypy ≥1.10 (modo estricto) · types-PyYAML |
| **Linter / formatter** | ruff ≥0.5 |
| **Estructura** | `src/smart_api_search/` (src layout) · `tests/` |
