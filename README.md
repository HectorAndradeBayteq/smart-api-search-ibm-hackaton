# Smart API Search (SmAS)

**IBM TechXchange 2026 Pre-conference Dev Day Hackathon**  
Built with **IBM Bob 2.0** · Developer workflow: **onboarding** and **API integration / application maintenance**

> The API you need probably already exists. If you do not know what it is called, it is almost as if it did not exist.

Smart API Search turns a corporate API catalog into **intent-searchable knowledge** and exposes it to IBM Bob through an MCP server. Developers describe what they need in natural language, inside the IDE. Bob finds the right operation, retrieves the real specification, and helps implement the integration.

This repository is the working proof-of-concept. It is written in English to comply with the official hackathon rules.

---

## Start here (judges and AI Submission Advisor)

The AI Submission Advisor and the judges look for four things. Use these links:

| What is reviewed | Where it is |
| --- | --- |
| Working implementation | [`src/smart_api_search/`](src/smart_api_search/) |
| How IBM Bob was used (written evidence) | [How IBM Bob 2.0 was used](#how-ibm-bob-20-was-used) |
| IBM Bob task session summary screenshots | [`bob_sessions/`](bob_sessions/) |
| Problem, users, uniqueness, and impact | [Problem](#the-problem) · [Solution](#the-solution) · [Impact](#measurable-impact) |
| Runnable prototype (ingest + MCP + Bob) | [Run the prototype](#run-the-prototype) |
| IBM Bob MCP registration | [Register the MCP server in IBM Bob](#register-the-mcp-server-in-ibm-bob) |
| No secrets in the repo | [Security](#security) · [`.env.example`](.env.example) · [`.gitignore`](.gitignore) · [`.bobignore`](.bobignore) |

---

## The problem

In a mid-size or large company, integrations are already documented: API portals, OpenAPI specs, and catalogs maintained by platform teams. That knowledge still fails at the moment a developer decides *which* API to call.

Developers think in intent (“I need customer information”, “I need to register a movement”). Catalogs answer with service names, operationIds, and exact paths. The result is a repeated, expensive loop:

1. Leave the IDE and browse the portal.
2. Pick a service by name similarity, not by what it actually does.
3. Copy the spec into code by hand — wrong parameters, wrong security, rework.
4. When in doubt, interrupt another team and ask them to re-explain documentation that already exists.

The cost is not only time. Integrations get duplicated, the wrong service is consumed, onboarding of every new developer is delayed, and the platform team becomes a human FAQ.

**One problem, solved well:** close the gap between developer intent and the correct specification, without leaving the development environment.

---

## The solution

**Smart API Search (SmAS)** converts the enterprise API catalog into a semantic knowledge base and publishes it as an MCP (Model Context Protocol) server that IBM Bob consumes from the IDE.

It works in four moves:

1. **Understand.** OpenAPI / Swagger specs are parsed into operations: purpose, data, security, and category. Incomplete technical text is enriched into a functional description that can be searched by intent.
2. **Index.** Each operation is stored in a hybrid vector collection (dense embeddings + BM25), so retrieval does not depend on knowing the exact service name.
3. **Serve.** An HTTP MCP server exposes that knowledge with a stable contract: search by intent, then fetch the technical spec on demand.
4. **Consume.** IBM Bob queries SmAS from the developer’s workspace, presents candidate operations with a functional explanation, and uses the real spec to write the integration.

Target users are **application developers** (especially people new to a large catalog) and **platform teams** who today answer the same “which API do I use?” questions.

Interaction stays inside the IDE:

1. The developer states a need in natural language.
2. Bob calls `search_openapi` and returns ranked candidates with a functional explanation, category, and official catalog link when available.
3. The developer chooses by meaning, not by name resemblance.
4. On request, Bob calls `get_endpoint_spec` and receives the endpoint, parameters, and structures required to implement the call.
5. Bob writes the integration against that specification as source of truth.

**What is unique:** this is not a portal with a better search box, and it is not a one-off code snippet. Bob **builds** a permanent context capability; every later project that Bob assists starts with the catalog already understood. The same knowledge is reusable across IBM Bob, VS Code, Cursor, and GitHub Copilot because the contract is MCP, not an IDE plugin.

---

## Architecture

```text
 Developer IDE (IBM Bob)
         │  MCP streamable-http
         ▼
 ┌───────────────────────────────┐
 │  MCP server                   │
 │  search_openapi               │
 │  get_endpoint_spec            │
 │  prompt: find_backend_api     │
 └───────────────┬───────────────┘
                 │
                 ▼
 ┌───────────────────────────────┐     ┌──────────────────────────┐
 │  Hybrid retrieval             │     │  Ingest pipeline         │
 │  HyDE → dense + BM25 → RRF    │◄────│  Portal or local files   │
 └───────────────┬───────────────┘     │  Parse → enrich → index  │
                 │                     └────────────┬─────────────┘
                 ▼                                  │
         Qdrant (hybrid collection)                 │
         dense + sparse (BM25)                      │
                                                    ▼
                              IBM API Connect Developer Portal
                              and/or local OpenAPI / Swagger files
```

| Piece | What it does | Code |
| --- | --- | --- |
| Ingest and interpretation | Reads specs from IBM Developer Portal or local files; extracts operations; enriches incomplete docs | [`src/smart_api_search/cli/ingest.py`](src/smart_api_search/cli/ingest.py) |
| Semantic knowledge base | Hybrid index: dense embeddings + BM25, fused with RRF; optional HyDE query expansion | [`src/smart_api_search/domain/`](src/smart_api_search/domain/) · [`src/smart_api_search/shared/embeddings.py`](src/smart_api_search/shared/embeddings.py) |
| MCP server | Publishes search and spec lookup as a service (`http://127.0.0.1:8000/mcp`) | [`src/smart_api_search/server.py`](src/smart_api_search/server.py) |
| IBM Bob | Consumes the MCP tools from the IDE and implements the integration | [`.bob/mcp.json`](.bob/mcp.json) |

Two adoption choices:

- **It is a service, not an install.** Each developer connects by configuration. No per-project clone of the catalog.
- **The contract stays stable as it scales.** What runs locally as a PoC can be published as an internal service without changing how agents consume it.

Embedding provider is configurable ([ADR-014](docs/adr/ADR-014-proveedor-embeddings-openai-watsonx.md)): **OpenAI** (`text-embedding-3-large`) or **IBM watsonx.ai** (`ibm/granite-embedding-278m-multilingual`).

**Related demo:** [`src/documentation-alternative`](src/documentation-alternative/README.md) shows the upstream path when an API has no documentation yet — a Bob documenter agent turns undocumented .NET code into OpenAPI and publishes it to a Developer Portal, after which Smart API Search ingests it with the same pipeline as any other catalog source.

---

## How IBM Bob 2.0 was used

IBM Bob is both **the builder of this capability** and **the runtime consumer** of it. The hackathon theme asks for Agent mode, parallel subagents, and document understanding applied to a full workflow — not only code completion. That is how this project was built.

### Document understanding

Bob read corporate-style OpenAPI / Swagger specifications (and portal-oriented catalog structure), identified operations, purpose, inputs/outputs, and security, and turned incomplete technical text into functional descriptions used at index time. Without that step, intent search has nothing useful to match against.

Evidence in code:

- [`src/smart_api_search/cli/ingest.py`](src/smart_api_search/cli/ingest.py) — parse operations, presentation metadata
- [`src/smart_api_search/domain/enricher.py`](src/smart_api_search/domain/enricher.py) — LLM enrichment of each operation
- [`config/categories.yaml`](config/categories.yaml) — category presentation metadata

### Agent mode

In Agent mode Bob designed and implemented the end-to-end capability:

- ingest from IBM Developer Portal and from local OpenAPI files
- hybrid semantic search (HyDE + dense + BM25 + RRF)
- MCP HTTP server with `search_openapi`, `get_endpoint_spec`, and the `find_backend_api` prompt
- tests and quality gates (pytest, ruff, mypy)

Evidence in code:

- [`src/smart_api_search/server.py`](src/smart_api_search/server.py)
- [`src/smart_api_search/domain/retrieval.py`](src/smart_api_search/domain/retrieval.py)
- [`tests/`](tests/)
- [`docs/specs/user-stories/`](docs/specs/user-stories/) — stories and tasks Bob executed against

### Subagents and parallel tasks

Work was split into coordinated fronts that Bob could run as independent tasks: catalog discovery, operation extraction, enrichment and indexing, hybrid retrieval, MCP exposure, and verification. That same split is how the solution scales: adding a catalog is a repeatable ingest, not a new project.

Evidence in specs (one story per front):

- [`docs/specs/user-stories/US-001-conexion-descubrimiento-portal/`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/)
- [`docs/specs/user-stories/US-002-extraccion-endpoints-metadatos/`](docs/specs/user-stories/US-002-extraccion-endpoints-metadatos/)
- [`docs/specs/user-stories/US-003-enriquecimiento-indexacion-ingesta/`](docs/specs/user-stories/US-003-enriquecimiento-indexacion-ingesta/)
- [`docs/specs/user-stories/US-004-busqueda-hibrida-hyde-rrf/`](docs/specs/user-stories/US-004-busqueda-hibrida-hyde-rrf/)
- [`docs/specs/user-stories/US-005-servidor-mcp-http/`](docs/specs/user-stories/US-005-servidor-mcp-http/)

### IBM watsonx.ai

watsonx.ai is an optional embedding backend for the knowledge base (`EMBED_PROVIDER=watsonx`, model `ibm/granite-embedding-278m-multilingual`). Configuration: [`.env.example`](.env.example). Implementation: [`src/smart_api_search/shared/embeddings.py`](src/smart_api_search/shared/embeddings.py). watsonx Orchestrate is not part of this submission.

### Required screenshots

Official rules require **each team member’s IBM Bob task session summary screenshots** in this repository. Live Bob session files must not be committed. Exported summaries belong here:

**[`bob_sessions/`](bob_sessions/)** — see that folder’s README for the naming convention.

---

## Measurable impact

We compare workflows, not unaudited percentages. The demo is the measurement surface.

| Situation | Without SmAS | With SmAS |
| --- | --- | --- |
| Find the right operation | Browse the portal, search by name, ask another team | One natural-language question in the IDE |
| Obtain the specification | Manual copy from the portal | Delivered by Bob from the indexed source |
| Configure the call | Trial and error on parameters and security | Generated from the real spec |

**What we measure in the demonstration:** time to identify the correct operation, number of questions resolved without leaving the IDE, and configuration errors avoided by using the indexed spec instead of a manual transcription.

Effects for the organization:

- **Less duplication** — if the existing service is found, a second one is not built.
- **Fewer integration errors** — implementation is based on the real spec.
- **Faster onboarding** — a new developer asks in natural language instead of memorizing the catalog.
- **A reusable AI asset** — the catalog becomes permanent context for every later Bob-assisted project.

---

## Review map (relative paths)

Artifacts the AI Submission Advisor and judges are expected to inspect.

### Implementation (working PoC)

| Path | Why it is reviewed |
| --- | --- |
| [`src/smart_api_search/server.py`](src/smart_api_search/server.py) | MCP server: tools, prompt, ASGI app |
| [`src/smart_api_search/cli/ingest.py`](src/smart_api_search/cli/ingest.py) | Catalog ingest (portal + local files), OpenAPI parse |
| [`src/smart_api_search/domain/enricher.py`](src/smart_api_search/domain/enricher.py) | LLM enrichment of operations |
| [`src/smart_api_search/domain/indexer.py`](src/smart_api_search/domain/indexer.py) | Hybrid index write |
| [`src/smart_api_search/domain/retrieval.py`](src/smart_api_search/domain/retrieval.py) | HyDE + dense + BM25 + RRF search |
| [`src/smart_api_search/domain/result.py`](src/smart_api_search/domain/result.py) | Search result composition (no full spec until asked) |
| [`src/smart_api_search/shared/embeddings.py`](src/smart_api_search/shared/embeddings.py) | OpenAI / watsonx.ai embedding provider |
| [`src/smart_api_search/config.py`](src/smart_api_search/config.py) | Settings from environment (no hardcoded secrets) |
| [`config/categories.yaml`](config/categories.yaml) | Category presentation metadata |
| [`start-server.ps1`](start-server.ps1) | Local MCP startup (ASGI: `smart_api_search.server:app`) |
| [`pyproject.toml`](pyproject.toml) | Package, CLI entry points, quality gates |
| [`tests/`](tests/) | Automated verification of the prototype |

### IBM Bob in the product (runtime)

| Path | Why it is reviewed |
| --- | --- |
| [`.bob/mcp.json`](.bob/mcp.json) | IBM Bob MCP client config (`smart-api-search`) |
| [`.github/copilot-mcp.json`](.github/copilot-mcp.json) | Same capability in GitHub Copilot |
| [`bob_sessions/`](bob_sessions/) | **Required** exported Bob task session summaries |

### How the solution was specified and decided (Bob as builder)

| Path | Why it is reviewed |
| --- | --- |
| [`docs/specs/technical-docs/smart-api-search.md`](docs/specs/technical-docs/smart-api-search.md) | Technical design of the capability |
| [`docs/adr/`](docs/adr/) | Architecture decisions (MCP, Qdrant, HyDE, watsonx, ASGI, …) |
| [`docs/specs/user-stories/US-001-conexion-descubrimiento-portal/`](docs/specs/user-stories/US-001-conexion-descubrimiento-portal/) | Portal connection and API discovery |
| [`docs/specs/user-stories/US-002-extraccion-endpoints-metadatos/`](docs/specs/user-stories/US-002-extraccion-endpoints-metadatos/) | Operation extraction and metadata |
| [`docs/specs/user-stories/US-003-enriquecimiento-indexacion-ingesta/`](docs/specs/user-stories/US-003-enriquecimiento-indexacion-ingesta/) | Enrichment, hybrid index, file ingest |
| [`docs/specs/user-stories/US-004-busqueda-hibrida-hyde-rrf/`](docs/specs/user-stories/US-004-busqueda-hibrida-hyde-rrf/) | Natural-language hybrid search |
| [`docs/specs/user-stories/US-005-servidor-mcp-http/`](docs/specs/user-stories/US-005-servidor-mcp-http/) | MCP HTTP server, tools, IBM Bob setup |

### Security (IBM Cloud account protection)

| Path | Why it is reviewed |
| --- | --- |
| [`.env.example`](.env.example) | Credential placeholders only |
| [`.gitignore`](.gitignore) | Blocks `.env`, keys, live AI session files |
| [`.bobignore`](.bobignore) | Stops Bob from logging credential patterns |
| [`SECURITY.MD`](SECURITY.MD) | Hackathon credential rules |

`.env` is never committed. If IBM Cloud credentials are detected in this repository, the IBM Cloud account may be suspended.

---

## Run the prototype

Requirements: **Python 3.12+**, a Qdrant instance (Qdrant Cloud or compatible), and an embedding provider key (OpenAI and/or watsonx.ai).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e . -r requirements-dev.txt
copy .env.example .env
```

Edit `.env` with your own values. Do not commit it.

### 1. Ingest a catalog

Local OpenAPI / Swagger files (`.json`, `.yaml`, `.yml`):

```powershell
smart-api-ingest --source files --specs-dir .\specs
```

IBM API Connect Developer Portal (when portal credentials are configured):

```powershell
smart-api-ingest --source portal
```

Useful flags: `--list-only`, `--dry-run`, `--no-enrich`, `--recreate --yes`, `--force`.

### 2. Start the MCP server

```powershell
.\start-server.ps1
```

Default URL: `http://127.0.0.1:8000/mcp`. Override with `MCP_HOST` / `MCP_PORT` if needed.

The server is always started by ASGI reference (`uvicorn smart_api_search.server:app`). Do not run the module as `__main__` ([ADR-013](docs/adr/ADR-013-arranque-servidor-mcp-asgi.md)).

### 3. Ask Bob in natural language

With the server running and [`.bob/mcp.json`](.bob/mcp.json) loaded, a developer can say:

> I need to look up customer information for onboarding.

Bob uses `search_openapi`, then `get_endpoint_spec` only when the developer is ready to implement.

### Tests

```powershell
pytest
```

---

## Register the MCP server in IBM Bob

1. Keep [`.bob/mcp.json`](.bob/mcp.json) as provided in this repository.
2. Start the server with [`start-server.ps1`](start-server.ps1).
3. In IBM Bob the server appears as `smart-api-search` with tools `search_openapi`, `get_endpoint_spec`, and prompt `find_backend_api`.

Configuration (`.bob/mcp.json`):

```json
{
  "mcpServers": {
    "smart-api-search": {
      "type": "streamable-http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### Other MCP-compatible IDEs

| IDE | Config file | Notes |
| --- | --- | --- |
| **IBM Bob** | [`.bob/mcp.json`](.bob/mcp.json) | Required for this hackathon demo |
| **GitHub Copilot** | [`.github/copilot-mcp.json`](.github/copilot-mcp.json) | Included |
| **VS Code** | MCP `servers` entry with `"type": "http"` and the same URL | Same contract |

### Tools and prompt

| Name | Role |
| --- | --- |
| `search_openapi(query, top_k=5)` | Intent search. Compact markdown candidates — not the full OpenAPI JSON |
| `get_endpoint_spec(spec_ref)` | Full operation fragment, call URL, and catalog deeplink |
| `find_backend_api(need)` | Guided flow: search → present → fetch spec only if the user asks |

---

## Scope of this delivery

**Demonstrated:** catalog interpretation and enrichment with Bob, hybrid semantic knowledge base, operating MCP server, consumption from the IDE, assistance implementing an integration from the real spec.

**Natural next steps (not claimed as done):** more catalogs, pre-integration access checks, and a permanently hosted corporate service.

Hackathon data rules: public data may be used when the terms allow commercial use; no client data, no personal data, no social-media scraping. Sample / synthetic API catalogs are used for the demonstration.

---

## Judging alignment

| Criterion (5 pts each) | How this submission addresses it |
| --- | --- |
| **Completeness and feasibility** | End-to-end PoC: ingest → index → MCP → Bob in the IDE. IBM tech is explicit: Bob 2.0 (build + consume), optional watsonx.ai embeddings, IBM Developer Portal ingest. |
| **Creativity and innovation** | Bob does not receive a search plugin; Bob **creates** a reusable catalog-context capability and then uses it. Intent search over names; spec delivered only on demand. |
| **Design and usability** | No extra UI to learn. MCP config is one file. Natural-language in the IDE. Results explain function first; JSON only when requested. |
| **Effectiveness and efficiency** | Targets a high-cost developer workflow (find + integrate the right API). Impact is shown as time, rework, and team dependency removed, and as a capability that scales to more catalogs without redesign. |

---

## Security

This repo started from the IBM Hackathon GitHub template so credentials are not committed.

- Copy [`.env.example`](.env.example) to `.env` and fill in local secrets.
- Never commit `.env`, API keys, or IBM Cloud credentials.
- Never paste secrets into Bob prompts. Use environment variables.
- Before every commit, review `git diff` and confirm `.env` is not staged.

Details: [`SECURITY.MD`](SECURITY.MD).

---

## License and originality

All implementation work for this submission is produced during the official hackathon window by Bayteq Team.
