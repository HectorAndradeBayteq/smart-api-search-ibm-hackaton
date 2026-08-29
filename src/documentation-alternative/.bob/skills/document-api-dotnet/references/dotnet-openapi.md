# OpenAPI generation in ASP.NET Core

All code on this page is verified against **.NET 10 SDK 10.0.400** with
`Microsoft.AspNetCore.OpenApi 10.0.11`, on a controllers project.

## 1. Package

```powershell
dotnet add src/Contoso.Orders.Api package Microsoft.AspNetCore.OpenApi
```

`Microsoft.AspNetCore.OpenApi` is the Microsoft library and the default option in
.NET 9+. Swashbuckle remains valid for legacy projects; if the project already has
it, do not migrate unless asked.

Optional, only if the developer wants a browsable UI: `Scalar.AspNetCore`. Not
required to publish to the portal.

## 2. csproj

```xml
<PropertyGroup>
  <TargetFramework>net10.0</TargetFramework>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <!-- Remove when the full public surface is documented. -->
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>
```

`GenerateDocumentationFile` is what makes `///` comments reach the document. In
.NET 10 you **do not** need to call `IncludeXmlComments`: the package picks them up
automatically at compile time.

In .NET 8 / 9 with Swashbuckle you do need:

```csharp
options.IncludeXmlComments(Path.Combine(AppContext.BaseDirectory,
    $"{Assembly.GetExecutingAssembly().GetName().Name}.xml"));
```

## 3. Program.cs

```csharp
using Contoso.Orders.Api;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddApiDocumentation();   // custom extension, see below

var app = builder.Build();

app.MapOpenApi();                          // serves /openapi/v1.json
app.MapControllers();

app.Run();
```

## 4. Metadata no XML comment can provide

Real title, functional description, contact, servers, and security are added with a
**document transformer**:

```csharp
using System.Text.Json.Nodes;
using Contoso.Orders.Api.Models;
using Microsoft.OpenApi;          // NOTE: in .NET 10 Microsoft.OpenApi.Models does NOT exist

namespace Contoso.Orders.Api;

public static class OpenApiSetup
{
    public static IServiceCollection AddApiDocumentation(this IServiceCollection services)
    {
        services.AddOpenApi(options =>
        {
            options.AddDocumentTransformer((document, context, cancellationToken) =>
            {
                document.Info = new OpenApiInfo
                {
                    Title = "Contoso Orders API",
                    Version = "1.0.0",
                    Description =
                        "Customer lookup and financial movement registration. " +
                        "Use to get a customer's commercial profile and to " +
                        "register charges, refunds, and adjustments on their account.",
                    Contact = new OpenApiContact
                    {
                        Name = "Integrations Team",
                        Email = "integraciones@contoso.example"
                    }
                };

                document.Servers = [new OpenApiServer { Url = "https://api.contoso.example" }];

                document.Components ??= new OpenApiComponents();
                document.Components.SecuritySchemes ??= new Dictionary<string, IOpenApiSecurityScheme>();
                document.Components.SecuritySchemes["bearerAuth"] = new OpenApiSecurityScheme
                {
                    Type = SecuritySchemeType.Http,
                    Scheme = "bearer",
                    Description = "Access token issued by the corporate identity provider."
                };

                document.Security =
                [
                    new OpenApiSecurityRequirement
                    {
                        [new OpenApiSecuritySchemeReference("bearerAuth", document)] = new List<string>()
                    }
                ];

                return Task.CompletedTask;
            });
        });

        return services;
    }
}
```

Per-model examples with a schema transformer (optional; improves portal card quality):

```csharp
options.AddSchemaTransformer((schema, context, cancellationToken) =>
{
    if (context.JsonTypeInfo.Type == typeof(PartyDto))
    {
        schema.Example = new JsonObject
        {
            ["id"] = "P-1001",
            ["name"] = "Marta Sanchez",
            ["segment"] = "retail",
            ["status"] = "active"
        };
    }

    return Task.CompletedTask;
});
```

## 5. Annotating an action

```csharp
/// <summary>Look up a customer's commercial profile by identifier.</summary>
/// <remarks>
/// Returns name, document id, commercial segment, and customer status.
/// This is the operation to use when you need "customer information"
/// before invoicing, collecting payment, or enabling a service.
/// </remarks>
/// <param name="id">Internal customer identifier, format P-#### (example: P-1001).</param>
/// <response code="200">Customer found.</response>
/// <response code="404">No customer exists with that identifier.</response>
[HttpGet("{id}")]
[EndpointName("GetPartyById")]
[Tags("Customers")]
[ProducesResponseType<PartyDto>(StatusCodes.Status200OK)]
[ProducesResponseType<ErrorDto>(StatusCodes.Status404NotFound)]
public IActionResult Get(string id)
```

Verified mapping to the generated document:

| In code | In OpenAPI |
| --- | --- |
| `<summary>` | `summary` |
| `<remarks>` | `description` |
| `<param>` | `parameters[].description` |
| `<response code="200">` | `responses.200.description` |
| `[EndpointName("...")]` | `operationId` |
| `[Tags("...")]` | `tags` |
| `[ProducesResponseType<T>]` | `responses.<code>.content.schema` |

## 6. Known pitfalls

- **`Microsoft.OpenApi.Models` does not exist in .NET 10.** The model was flattened to
  `Microsoft.OpenApi`. If you see `CS0234: The type or namespace name 'Models' does
  not exist`, remove that `using`.
- **`SecuritySchemes` is `IDictionary<string, IOpenApiSecurityScheme>`** (interface),
  not `OpenApiSecurityScheme`. Declaring it with the concrete type does not compile.
- **Referencing a security scheme** is done with
  `new OpenApiSecuritySchemeReference("bearerAuth", document)`, not a loose object.
- **Authentication middleware can hide the document.** If `GET /openapi/v1.json`
  returns 401, export with a token or exclude the route.
- **Default `info.title` is the assembly name** (`Contoso.Orders.Api | v1`) and there
  is no `info.description`. Without the transformer in section 4, the spec fails the
  portal quality gate.
- **The document is generated at runtime**, with the app running. Editing
  `openapi.json` by hand does not help: it is lost on the next export.
