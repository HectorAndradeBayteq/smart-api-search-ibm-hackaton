# How to write documentation that is searchable

Documentation in this project has a concrete consumer: the Smart API Search ingest
pipeline, which indexes the meaning of each operation so a developer can find it by
asking in natural language.

From that comes the only criterion that matters:

> If someone describes a business need without knowing the API, the written
> description must be enough to choose this operation and reject similar ones.

## Good and bad

**Bad — repeats the method name.**

```csharp
/// <summary>Gets a party by id.</summary>
```

That is already visible in the signature. It adds nothing indexable.

**Good — says what it represents and when to use it.**

```csharp
/// <summary>Look up a customer's commercial profile by identifier.</summary>
/// <remarks>
/// Returns name, document id, commercial segment, and customer status.
/// Use when you need customer information before invoicing, collecting payment,
/// or enabling a service. Does not include movements or balances.
/// </remarks>
```

Three things make the difference: it translates the technical name (`party` →
customer), says **when** to use it, and says what it does **not** do.

## Five rules

1. **Translate internal names.** `party`, `movement`, `doc` are vocabulary from the
   team that wrote the API. Document in the vocabulary of who will consume it.
2. **Start the summary with an infinitive verb.** "Look up", "Register", "Cancel".
   It reads the same in a portal list and in a search result.
3. **Explicitly say what the operation does NOT do** when a similar one exists. That
   is what prevents picking the wrong endpoint by name similarity.
4. **Real examples, not `string`.** `P-1001`, not "identifier". A concrete format
   saves trial and error when integrating.
5. **Document errors as part of the contract.** What a 404 means, when a 409 appears,
   which error code the body carries.

## What not to do

- **Do not invent.** If the code does not tell you whether a field is optional, or
  what a status means, mark it as pending confirmation and report it. An invented
  description is worse than none: it gets indexed and spreads.
- **Do not document business values that are not in the code** (limits, SLAs,
  prices). The owning team confirms those.
- **Do not copy the same description across operations.** If two operations share the
  same description, semantic search cannot tell them apart: that is exactly the
  problem this project solves.

## Checklist before publishing

Same criteria applied by `devportal_validate_spec`. Blockers in **bold**.

Document:

- [ ] **Readable `info.title`** (not the assembly name).
- [ ] **Functional `info.description`**, at least 40 characters.
- [ ] **`info.version` declared.**
- [ ] **`components.securitySchemes` present.**
- [ ] `info.contact` with the responsible team.
- [ ] `servers` with the base URL.

Each operation:

- [ ] **`summary`.**
- [ ] **Functional `description`**, at least 30 characters.
- [ ] **Unique `operationId`.**
- [ ] **Every parameter has a `description`.**
- [ ] **`requestBody` has a `description`** when it exists.
- [ ] **At least one documented 2xx response.**
- [ ] **Every response has a `description`.**
- [ ] **Security requirement declared** (global or per operation).
- [ ] Domain `tags`.
- [ ] At least one documented 4xx error response.
- [ ] Example on requestBody and on the main response.

## Final test

Read an operation's `summary` + `description` **without seeing the path or method
name**. If it is still unclear what it is for, it is not documented yet.
