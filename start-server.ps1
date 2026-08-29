# start-server.ps1
# Arranca el servidor MCP de smart-api-search usando el Python del entorno virtual.
# Uso: .\start-server.ps1 [-ServerHost 127.0.0.1] [-Port 8000] [-McpPath /mcp]
#
# El servidor se expone por referencia ASGI (ver ADR-013):
#   uvicorn smart_api_search.server:app --host ... --port ...
# NO ejecutar el modulo como __main__ — ver RF-06.9.

param(
    [string]$ServerHost = "",
    [int]$Port = 0,
    [string]$McpPath = ""
)

if (-not $ServerHost) {
    if ($env:MCP_HOST) { $ServerHost = $env:MCP_HOST } else { $ServerHost = "127.0.0.1" }
}
if (-not $Port) {
    if ($env:MCP_PORT) { $Port = [int]$env:MCP_PORT } else { $Port = 8000 }
}
if (-not $McpPath) {
    if ($env:MCP_PATH) { $McpPath = $env:MCP_PATH } else { $McpPath = "/mcp" }
}

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Entorno virtual no encontrado. Ejecuta: python -m venv .venv; .venv\Scripts\pip install -e ."
    exit 1
}

Write-Host "Arrancando servidor MCP en http://${ServerHost}:${Port}${McpPath} ..." -ForegroundColor Cyan
& $VenvPython -m uvicorn smart_api_search.server:app --host $ServerHost --port $Port
