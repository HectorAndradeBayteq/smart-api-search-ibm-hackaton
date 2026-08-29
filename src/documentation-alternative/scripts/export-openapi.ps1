<#
.SYNOPSIS
  Levanta el API, descarga el documento OpenAPI generado y apaga el proceso.

.DESCRIPTION
  Fase 4 del procedimiento: la documentacion no vale hasta que se ve en el
  documento OpenAPI. Este script compila, ejecuta el proyecto en un puerto
  temporal, guarda /openapi/v1.json en artifacts/ y detiene la aplicacion.

  El API de ejemplo exige un bearer token en todas las rutas, incluida la del
  documento; por eso se envia -Token. Si el proyecto excluye la ruta del
  documento de su middleware de autenticacion, el token se ignora.

.EXAMPLE
  pwsh scripts/export-openapi.ps1
  pwsh scripts/export-openapi.ps1 -Port 5320 -Output artifacts/openapi.json
#>
[CmdletBinding()]
param(
    [string]$Project = "src/Contoso.Orders.Api",
    [int]$Port = 5217,
    [string]$Output = "artifacts/openapi.json",
    [string]$DocumentPath = "/openapi/v1.json",
    [string]$Token = "demo-token",
    [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$projectPath = Join-Path $root $Project
$outputPath = Join-Path $root $Output
$url = "http://localhost:$Port$DocumentPath"

New-Item -ItemType Directory -Force -Path (Split-Path $outputPath) | Out-Null

Write-Host "Compilando $Project ..." -ForegroundColor Cyan
dotnet build $projectPath -v q --nologo
if ($LASTEXITCODE -ne 0) { throw "La compilacion fallo; corrige los errores antes de exportar." }

Write-Host "Levantando el API en el puerto $Port ..." -ForegroundColor Cyan
$logPath = Join-Path $root "artifacts/api-run.log"
$process = Start-Process -FilePath "dotnet" `
    -ArgumentList @("run", "--project", $projectPath, "--urls", "http://localhost:$Port") `
    -PassThru -NoNewWindow -RedirectStandardOutput $logPath -RedirectStandardError "$logPath.err"

try {
    $headers = @{ Authorization = "Bearer $Token" }
    $document = $null
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        if ($process.HasExited) {
            throw "El API termino inesperadamente. Revisa $logPath"
        }

        try {
            $document = Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing -TimeoutSec 5
            break
        } catch {
            Start-Sleep -Milliseconds 700
        }
    }

    if (-not $document) {
        throw "No se pudo obtener $url en $TimeoutSeconds s. Revisa $logPath y que MapOpenApi() este registrado."
    }

    # Se reescribe con indentacion: el documento viaja al portal y lo lee gente.
    # Sin BOM: Windows PowerShell 5.1 lo agrega con -Encoding utf8 y hay parsers
    # de OpenAPI que lo rechazan.
    $json = $document.Content | ConvertFrom-Json
    $text = $json | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($outputPath, $text, (New-Object System.Text.UTF8Encoding($false)))

    $operations = 0
    foreach ($path in $json.paths.PSObject.Properties) {
        $operations += @($path.Value.PSObject.Properties | Where-Object {
            $_.Name -in @("get", "put", "post", "delete", "patch", "head", "options", "trace")
        }).Count
    }

    Write-Host ""
    Write-Host "Documento guardado en: $outputPath" -ForegroundColor Green
    Write-Host "  openapi: $($json.openapi)"
    Write-Host "  title:   $($json.info.title) $($json.info.version)"
    Write-Host "  operaciones: $operations"
    Write-Host ""
    Write-Host "Siguiente paso: devportal_validate_spec con spec_path=$outputPath" -ForegroundColor Cyan
}
finally {
    if (-not $process.HasExited) {
        Write-Host "Deteniendo el API (PID $($process.Id)) ..." -ForegroundColor DarkGray
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
}
