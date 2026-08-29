# Documenting an API that has no documentation

Smart API Search (SmAS) searches a catalog of **published** OpenAPI specs. Many
organizations still have working APIs with no usable documentation. This sample
closes that gap: IBM Bob documents an undocumented .NET API, publishes the
resulting OpenAPI to a Developer Portal, and hands that source to the same SmAS
ingest path used for any other catalog entry.

> Open this folder (`src/documentation-alternative/`) as its own project in IBM Bob — not the Smart API Search repo root — so Bob loads the agent, skill, and MCP here; this sample is separate from the SmAS product.

```
┌──────────────────────────────────────────────────────────────────┐
│  This sample (documentation-alternative)                         │
│                                                                  │
│  Undocumented .NET API                                           │
│            │                                                     │
│            ▼                                                     │
│  Bob documenter agent  +  document-api-dotnet skill              │
│            │                                                     │
│            ▼                                                     │
│  openapi.json  →  quality gate (devportal MCP)                   │
│            │                                                     │
│            ▼                                                     │
│  IBM Developer Portal (published catalog source)                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │  same ingest contract as any portal
                             │  or local OpenAPI / Swagger file
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  Smart API Search (main solution)                                │
│                                                                  │
│  Ingest → enrich → hybrid index (dense + BM25 + RRF)             │
│            │                                                     │
│            ▼                                                     │
│  MCP server: search_openapi · get_endpoint_spec                  │
│            │                                                     │
│            ▼                                                     │
│  Developer IDE (IBM Bob): find by intent, integrate from the     │
│  real spec                                                       │
└──────────────────────────────────────────────────────────────────┘
```

Inside this folder the linear demo is:

```
undocumented .NET code → Bob documenter → openapi.json → MCP devportal → Developer Portal → SmAS ingest
                           skill: document-api-dotnet      quality gate
```

## What is here

| Path | What it is |
| --- | --- |
| `src/Contoso.Orders.Api/` | Working .NET 10 REST API with no documentation. Demo starting point. |
| `.bob/agents/api-documenter.md` | Documenter agent: how it works, where it stops, what it must not do. |
| `.bob/skills/document-api-dotnet/` | Five-phase procedure, verified .NET OpenAPI setup, writing criteria. |
| `mcp-devportal/` | MCP server that validates and publishes specs to the Developer Portal. |
| `scripts/audit-docs.ps1` | Phase 1: documentation inventory. |
| `scripts/export-openapi.ps1` | Phase 4: writes `artifacts/openapi.json` from the running app. |
| `portal-store/` | Simulated portal (`mock` mode). Created on publish. |

## Requirements

- .NET SDK 10 (`dotnet --version` verified with 10.0.400)
- Python 3.10+ (the MCP uses only the standard library)
- PowerShell (scripts are `.ps1`)

## Setup

Open **this directory** (`documentation-alternative/`) as the project in IBM Bob
so it loads the agent, the skill, and `.mcp.json`. Approve the `devportal` server
when prompted.

Confirm the MCP:

```
devportal_status
```

Expected: `mode: mock` and a `portal-store` path.

To run from the repository root instead, copy `.bob/agents/`, `.bob/skills/`, and
the `devportal` entry from `.mcp.json` to the root, then adjust `DEVPORTAL_STORE`
and `spec_path` values.

## Starting point

```powershell
dotnet run --project src/Contoso.Orders.Api --urls http://localhost:5217
curl -H "Authorization: Bearer demo" http://localhost:5217/api/v1/parties/P-1001
```

Two controllers, eight operations, names that hide intent: `PartyController`
returns **customers**; `MovementController` records **charges, refunds, and
adjustments**. There is no OpenAPI package, no `///` comments, and no response
attributes.

Baseline:

```powershell
pwsh scripts/audit-docs.ps1
```

Expected: 8 HTTP actions, 0% with comments, no documentation library.

## Demo steps

**1. Invoke the agent** in Bob:

> Use the api-documenter agent to document the API in `src/Contoso.Orders.Api`
> and publish it to the Developer Portal.

**2. Audit and confirm.** The agent runs `audit-docs.ps1`, reads the code, and
presents what it understood: business purpose, models, authentication, and
misleading names. It stops here for developer review.

**3. Install OpenAPI generation.** `Microsoft.AspNetCore.OpenApi`,
`GenerateDocumentationFile`, `AddOpenApi` / `MapOpenApi`, and a document
transformer (title, functional description, contact, servers, security scheme).

**4. Annotate.** XML comments (`summary`, `remarks`, `param`, `response`),
`[EndpointName]`, `[Tags]`, `[ProducesResponseType<T>]`, and model examples.

**5. Generate and validate.**

```powershell
pwsh scripts/export-openapi.ps1
```

```
devportal_validate_spec  spec_path=artifacts/openapi.json
```

If the portal rejects the spec, the agent fixes **source code** and regenerates.
`openapi.json` is not edited by hand.

**6. Publish with approval.** First `dry_run=true`, then:

```
devportal_publish_api  spec_path=artifacts/openapi.json  owner="Integrations Team"
```

Check with `devportal_list_apis`. Published content lands in `portal-store/apis/`
and `portal-store/catalog.json` — the catalog source SmAS ingest can consume.

## Reset

```powershell
git checkout -- src/Contoso.Orders.Api
Remove-Item -Recurse -Force artifacts, portal-store -ErrorAction SilentlyContinue
```

Then call `devportal_unpublish_api` with the published name and version.

## Mock vs real portal

The MCP supports three modes. The demo uses `mock` (no network or credentials).
Switching to a real portal is configuration in `.mcp.json` only; the agent
procedure stays the same. Details:
[mcp-devportal/README.md](mcp-devportal/README.md).

## Scope

This is a supervised, API-by-API demo. The same procedure, quality gate, and MCP
can be driven later by an orchestrator across many repositories; that scale-out
is out of scope for this sample.
