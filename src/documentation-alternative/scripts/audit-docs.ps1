<#
.SYNOPSIS
  Inventario del estado de documentacion de un proyecto ASP.NET Core.

.DESCRIPTION
  Fase 1 del procedimiento: antes de escribir una sola linea de documentacion,
  el agente necesita saber que hay. Este script reporta:
    - paquetes de generacion de documentacion instalados
    - si el csproj emite el archivo XML de comentarios
    - si el pipeline expone el documento OpenAPI
    - cuantas acciones hay y cuantas tienen comentarios /// y atributos

  Es un inventario por analisis de texto, deliberadamente simple: sirve para
  decidir el trabajo, no para reemplazar la revision del agente.

.EXAMPLE
  pwsh scripts/audit-docs.ps1 -Project src/Contoso.Orders.Api
#>
[CmdletBinding()]
param(
    [string]$Project = "src/Contoso.Orders.Api"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$projectPath = Resolve-Path (Join-Path $root $Project)
$csproj = Get-ChildItem -Path $projectPath -Filter *.csproj | Select-Object -First 1

if (-not $csproj) {
    throw "No se encontro un .csproj en $projectPath"
}

$csprojText = Get-Content $csproj.FullName -Raw

Write-Host "== Proyecto ==" -ForegroundColor Cyan
Write-Host "  $($csproj.FullName)"
if ($csprojText -match "<TargetFramework>([^<]+)</TargetFramework>") {
    Write-Host "  TargetFramework: $($Matches[1])"
}

Write-Host ""
Write-Host "== Librerias de documentacion ==" -ForegroundColor Cyan

$docPackages = @(
    "Microsoft.AspNetCore.OpenApi",
    "Swashbuckle.AspNetCore",
    "NSwag.AspNetCore",
    "Scalar.AspNetCore"
)

$found = $false
foreach ($package in $docPackages) {
    if ($csprojText -match [regex]::Escape("Include=`"$package`"")) {
        Write-Host "  [instalado] $package" -ForegroundColor Green
        $found = $true
    }
}
if (-not $found) {
    Write-Host "  [falta] ninguna libreria de generacion de documentacion" -ForegroundColor Yellow
}

$hasDocFile = $csprojText -match "<GenerateDocumentationFile>\s*true\s*</GenerateDocumentationFile>"
$color = if ($hasDocFile) { "Green" } else { "Yellow" }
Write-Host "  GenerateDocumentationFile: $hasDocFile" -ForegroundColor $color

Write-Host ""
Write-Host "== Pipeline ==" -ForegroundColor Cyan

$programPath = Join-Path $projectPath "Program.cs"
if (Test-Path $programPath) {
    $program = Get-Content $programPath -Raw
    $checks = [ordered]@{
        "AddOpenApi / AddSwaggerGen" = ($program -match "AddOpenApi|AddSwaggerGen")
        "MapOpenApi / UseSwagger"    = ($program -match "MapOpenApi|UseSwagger")
        "Transformer de documento"   = ($program -match "AddDocumentTransformer")
    }
    foreach ($check in $checks.GetEnumerator()) {
        $mark = if ($check.Value) { "si" } else { "NO" }
        $c = if ($check.Value) { "Green" } else { "Yellow" }
        Write-Host ("  {0,-28} {1}" -f $check.Key, $mark) -ForegroundColor $c
    }
} else {
    Write-Host "  Program.cs no encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== Cobertura en el codigo ==" -ForegroundColor Cyan

$sources = Get-ChildItem -Path $projectPath -Filter *.cs -Recurse |
    Where-Object { $_.FullName -notmatch "\\(bin|obj)\\" }

$totalActions = 0
$documentedActions = 0
$typedResponses = 0
$rows = @()

foreach ($file in $sources) {
    $lines = Get-Content $file.FullName
    $fileActions = 0
    $fileDocumented = 0

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -notmatch '^\s*\[Http(Get|Post|Put|Patch|Delete)') { continue }

        $fileActions++
        $totalActions++

        # Mira hacia arriba: comentarios /// y atributos de respuesta del bloque.
        $hasDoc = $false
        $hasTyped = $false
        for ($j = $i - 1; $j -ge 0 -and $j -ge $i - 15; $j--) {
            $line = $lines[$j].Trim()
            if ($line -match '^///') { $hasDoc = $true }
            if ($line -match '^\[ProducesResponseType') { $hasTyped = $true }
            if ($line -eq "" -or $line -match '^\}') { break }
        }
        # Los atributos tambien pueden ir despues del [HttpX] y antes del metodo.
        for ($j = $i + 1; $j -lt $lines.Count -and $j -le $i + 10; $j++) {
            $line = $lines[$j].Trim()
            if ($line -match '^\[ProducesResponseType') { $hasTyped = $true }
            if ($line -match 'public ') { break }
        }

        if ($hasDoc) { $fileDocumented++; $documentedActions++ }
        if ($hasTyped) { $typedResponses++ }
    }

    if ($fileActions -gt 0) {
        $rows += [pscustomobject]@{
            Archivo      = $file.Name
            Acciones     = $fileActions
            ConComentario = $fileDocumented
        }
    }
}

if ($rows) { $rows | Format-Table -AutoSize | Out-String | Write-Host }

$pct = if ($totalActions -gt 0) { [math]::Round($documentedActions * 100 / $totalActions) } else { 0 }
Write-Host "  Acciones HTTP: $totalActions"
Write-Host "  Con comentarios ///: $documentedActions ($pct%)"
Write-Host "  Con [ProducesResponseType]: $typedResponses"

Write-Host ""
Write-Host "== Artefactos previos ==" -ForegroundColor Cyan
$existing = Get-ChildItem -Path $root -Include "openapi*.json", "swagger*.json" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\(bin|obj|portal-store)\\" }

if ($existing) {
    $existing | ForEach-Object { Write-Host "  $($_.FullName)" }
} else {
    Write-Host "  No hay documento OpenAPI generado todavia."
}

Write-Host ""
Write-Host "Next step: apply the document-api-dotnet skill procedure." -ForegroundColor Cyan
