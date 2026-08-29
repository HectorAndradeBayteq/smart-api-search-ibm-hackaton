---
name: document-api-dotnet
description: >-
  Procedure to document a .NET REST API that has no prior documentation and publish
  it to the Developer Portal. Covers project audit, installing the generation
  library (Microsoft.AspNetCore.OpenApi), annotating classes and methods with XML
  comments and attributes, generating the OpenAPI document, and publishing via the
  devportal MCP. Use when asked to document a .NET/ASP.NET Core API, add OpenAPI or
  Swagger to an existing project, improve endpoint documentation, or publish a spec
  to the API portal.
---

# Document an undocumented .NET API

Goal: an API operation can be found by **what it does**, not by what it is called.
That is the criterion used to judge the result, because the end consumer of this
documentation is the Smart API Search ingest pipeline.

The work has five phases. Do not skip phases: each one produces evidence the next
one needs.

## Golden rule

Never change API behavior. This task adds comments, attributes, metadata, and
documentation configuration. If documenting requires fixing logic, **stop and report
it to the developer**; do not fix it on your own.

Only allowed exception: expose the OpenAPI document route (see Phase 2), and only if
you call it out explicitly in the final report.

---

## Phase 1 · Audit before writing

```powershell
pwsh scripts/audit-docs.ps1 -Project src/Contoso.Orders.Api
```

The report says which library is present, whether the csproj emits the XML comments
file, whether the pipeline exposes the document, and how many actions are uncommented.

Also read the code and answer these four questions in writing before changing anything:

1. **What does this API do in business terms.** One sentence, no technical jargon.
2. **What each model represents.** A DTO named `PartyDto` may be "customer"; say so,
   do not repeat the class name.
3. **How authentication works.** Look for middleware, filters, or authorization
   attributes.
4. **Which operations have misleading names.** A `GET /parties/{id}` that actually
   returns a customer profile is exactly the case documentation must close.

Present these answers to the developer **before** documenting. If the agent is wrong
here, the documentation ends up plausible but false.

## Phase 2 · Install and configure generation

Full detail, with verified .NET 10 code, in
[references/dotnet-openapi.md](references/dotnet-openapi.md). Summary:

```powershell
dotnet add src/Contoso.Orders.Api package Microsoft.AspNetCore.OpenApi
```

In the `.csproj`: `<GenerateDocumentationFile>true</GenerateDocumentationFile>` and
`<NoWarn>$(NoWarn);1591</NoWarn>` while documentation is incomplete.

In `Program.cs`: `builder.Services.AddOpenApi(...)` and `app.MapOpenApi()`.

Add a **document transformer** with what no XML comment can provide: functional API
title and description, team contact, `servers`, and the security scheme. Without
this the spec fails the portal quality gate.

If authentication middleware blocks `/openapi/v1.json` (it does in this sample
project), two valid options: pass a token when exporting
(`export-openapi.ps1 -Token ...`) or exclude the route from the middleware. Prefer
the first unless the developer asks otherwise: it changes less code.

## Phase 3 · Annotate classes and methods

For each HTTP action, in the order they appear in the controller:

- `/// <summary>` — what it does, in business language, starting with a verb.
- `/// <remarks>` — when to use it, what it returns, constraints. This is where the
  intent phrase goes ("use when you need customer information").
- `/// <param>` — what each parameter is, with format and a real example.
- `/// <response code="...">` — one for each status code the method can return.
- `[EndpointName("...")]` — stable, unique operationId.
- `[Tags("...")]` — portal grouping in domain terms (`Customers`, not `PartyController`).
- `[ProducesResponseType<T>(StatusCodes.Status...)]` — real type for each response,
  including errors.

Also document DTO properties with `///`: that is what the consumer sees when choosing
the operation.

Writing criteria and good/bad examples in
[references/documentation-criteria.md](references/documentation-criteria.md).

## Phase 4 · Generate and verify the document

```powershell
pwsh scripts/export-openapi.ps1
```

Writes `artifacts/openapi.json`. Verify the file, not the intent: if a `summary`
does not appear there, for the portal it does not exist.

Then run the quality gate with the MCP tool:

```
devportal_validate_spec  spec_path=artifacts/openapi.json
```

It returns coverage, blockers, and warnings. **Iterate Phase 3 → Phase 4 until there
are no blockers.** Do not dress up the result by editing `openapi.json` by hand: the
document is regenerated from code and the change is lost.

## Phase 5 · Publish to the Developer Portal

Before publishing, confirm the destination:

```
devportal_status
```

Publish:

```
devportal_publish_api
  spec_path=artifacts/openapi.json
  owner="Integrations Team"
  tags=["Customers","Movements"]
  visibility=authenticated
```

Rules:

- **Publish only with explicit developer approval.** The demo is a supervised flow:
  show `dry_run=true` first, ask for confirmation, then publish.
- **Do not use `force=true`** to skip blockers. If the portal rejects, the correct
  response is to go back to Phase 3.
- Verify with `devportal_list_apis` and `devportal_get_api`.

## Final report

Always close with:

1. What was documented (operations and models touched).
2. Coverage before → after, with numbers from `audit-docs.ps1` and validation.
3. Ambiguities resolved by assumption, flagged for human review.
4. Where it was published.
5. What was **not** touched (business logic).
