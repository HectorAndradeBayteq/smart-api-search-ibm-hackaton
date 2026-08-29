# MCP `devportal`

MCP server that receives documentation produced by the agent and publishes it to
the Developer Portal. It implements JSON-RPC 2.0 over stdio with **only the Python
standard library**: nothing to install, and nothing that can break on demo day.

| File | Role |
| --- | --- |
| `server.py` | MCP protocol and tool definitions. |
| `spec_check.py` | Quality gate: decides whether a spec is documented enough. |
| `portal.py` | Publish adapters: `mock`, `apic`, `generic`. |

## Tools

| Tool | Purpose |
| --- | --- |
| `devportal_status` | Which portal, catalog, and credentials will be used. |
| `devportal_validate_spec` | Runs the quality gate without publishing. Iteration tool. |
| `devportal_publish_api` | Validates and publishes. Rejects on blockers. Supports `dry_run`. |
| `devportal_list_apis` | Lists published APIs, with documentation coverage and date. |
| `devportal_get_api` | Returns the published spec for verification. |
| `devportal_unpublish_api` | Removes a publication (cleanup between demos). |

## Quality gate

`devportal_publish_api` is not a disguised `POST`: before publishing it requires the
spec to be understandable. Coverage is the percentage of operations **with no
blockers**, and the default minimum is 80% (`threshold`).

Blockers: functional `info.description` (40+ characters), `info.title`,
`info.version`, `components.securitySchemes`, and per operation `summary`,
`description` (30+ characters), unique `operationId`, description for every
parameter and response, described `requestBody`, at least one 2xx response, and a
declared security requirement.

Warnings (do not block): `info.contact`, `servers`, `tags`, documented 4xx
response, examples on requestBody and responses.

`force=true` publishes despite blockers. It exists for exceptional cases with
explicit authorization; the agent is instructed not to use it.

## Configuration

Everything is environment variables in `.mcp.json`.

### `mock` (default, used in the demo)

Does not call any service: writes the spec under `portal-store/apis/` and maintains
the `portal-store/catalog.json` index. That index is the source Smart API Search
ingest can consume.

| Variable | Default | Meaning |
| --- | --- | --- |
| `DEVPORTAL_MODE` | `mock` | Operating mode. |
| `DEVPORTAL_STORE` | `../portal-store` | Simulated portal directory. |
| `DEVPORTAL_CATALOG` | `sandbox` | Target catalog name. |

### `apic` — IBM API Connect

```json
"env": {
  "DEVPORTAL_MODE": "apic",
  "DEVPORTAL_BASE_URL": "https://apic.example.com",
  "DEVPORTAL_ORG": "my-provider-org",
  "DEVPORTAL_CATALOG": "sandbox",
  "DEVPORTAL_TOKEN": "…",
  "DEVPORTAL_PUBLISH": "true"
}
```

Uploads the spec as a draft API to `POST /api/orgs/{org}/drafts/draft-apis`. With
`DEVPORTAL_PUBLISH=true` it also publishes a product in the catalog. Verify the
routes against the client's API Connect version before using it in production.

### `generic` — any REST portal

```json
"env": {
  "DEVPORTAL_MODE": "generic",
  "DEVPORTAL_BASE_URL": "https://portal.example.com/api",
  "DEVPORTAL_APIS_PATH": "/apis",
  "DEVPORTAL_TOKEN": "…"
}
```

`POST {BASE_URL}{APIS_PATH}` with `{name, version, catalog, visibility, owner, tags, openapi}`.

### Shared

| Variable | Default | Meaning |
| --- | --- | --- |
| `DEVPORTAL_TOKEN` | — | Sent as `Authorization: Bearer`. |
| `DEVPORTAL_TIMEOUT` | `30` | Seconds per HTTP request. |
| `DEVPORTAL_INSECURE` | `false` | `true` skips TLS validation (test environments only). |

## Try it without an MCP client

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"devportal_status","arguments":{}}}' \
  | python server.py
```

## Implementation notes

- `stdout` is reserved for the protocol; all logging goes to `stderr` with a
  `[devportal]` prefix.
- Responses are serialized as ASCII and streams are reconfigured to UTF-8: on
  Windows the console defaults to cp1252 and accented characters broke JSON-RPC.
- Portal errors return as `isError: true` with detail, not as a protocol exception:
  the agent can read them and correct course.
- Specs must be JSON. If the project generates YAML, convert it first.
