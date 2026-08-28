# start-server.ps1
# Arranca el servidor MCP de smart-api-search usando el Python del entorno virtual.
# Uso: .\start-server.ps1 [--host 127.0.0.1] [--port 8000] [--path /mcp]
#
# El servidor se expone por referencia ASGI (ver ADR-013):
#   uvicorn smart_api_search.server:app --host ... --port ...
# NO ejecutar el módulo como __main__ — ver RF-06.9.

param(
    [string]$Host = $env:MCP_HOST ?? "127.0.0.1",
    [int]$Port    = [int]($env:MCP_PORT ?? "8000"),
    [string]$Path = $env:MCP_PATH ?? "/mcp"
)

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Entorno virtual no encontrado. Ejecuta: python -m venv .venv && .venv\Scripts\pip install -e . -r requirements-dev.txt"
    exit 1
}

Write-Host "Arrancando servidor MCP en http://${Host}:${Port}${Path} ..." -ForegroundColor Cyan
& $VenvPython -m uvicorn smart_api_search.server:app --host $Host --port $Port
