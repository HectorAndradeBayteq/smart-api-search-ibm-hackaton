# Smart API Search — Servidor MCP HTTP

Búsqueda semántica híbrida sobre catálogos OpenAPI expuesta como servidor MCP HTTP. Permite a desarrolladores descubrir y consultar endpoints de API en lenguaje natural directamente desde cualquier IDE compatible con el protocolo MCP (IBM Bob, VS Code, Cursor, GitHub Copilot).

---

## Servidor MCP

### Arrancar el servidor

```powershell
# Windows (PowerShell) — usa el Python del entorno virtual
.\start-server.ps1
```

El servidor arranca en `http://127.0.0.1:8000/mcp` por defecto.
Puedes sobreescribir el host y el puerto con variables de entorno:

```powershell
$env:MCP_HOST = "0.0.0.0"; $env:MCP_PORT = "9000"; .\start-server.ps1
```

> **Importante (ADR-013):** el servidor se expone **siempre** por referencia ASGI
> (`uvicorn smart_api_search.server:app`). No ejecutes el módulo como `__main__`.

### Registrar el servidor en IBM Bob

1. El archivo [`.bob/mcp.json`](.bob/mcp.json) ya está incluido en el repositorio
   con la configuración lista para IBM Bob.
2. Arranca el servidor con `.\start-server.ps1`.
3. En IBM Bob, el servidor aparecerá como `smart-api-search` con las herramientas
   `search_openapi`, `get_endpoint_spec` y el prompt `find_backend_api`.

Configuración (`.bob/mcp.json`):

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

### Otros IDEs compatibles

| IDE | Archivo de configuración | Formato |
|-----|--------------------------|---------|
| **VS Code** | `.vscode/settings.json` → `mcpServers` | `"type": "streamable-http", "url": "http://127.0.0.1:8000/mcp"` |
| **Cursor** | [`.cursor/mcp.json`](.cursor/mcp.json) | Ya incluido en el repositorio |
| **GitHub Copilot** | [`.github/copilot-mcp.json`](.github/copilot-mcp.json) | Ya incluido en el repositorio |

### Herramientas expuestas

| Herramienta | Descripción |
|-------------|-------------|
| `search_openapi(query, top_k=5)` | Busca endpoints de API en lenguaje natural. Devuelve markdown compacto con los resultados. |
| `get_endpoint_spec(spec_ref)` | Recupera el fragmento OpenAPI completo de un endpoint por su `spec_ref`. |

### Prompt disponible

| Prompt | Descripción |
|--------|-------------|
| `find_backend_api(need)` | Guía el flujo completo: buscar → presentar resultados → pedir el spec si el usuario lo solicita. |

---

## IBM Hackathon GitHub Project Template

This GitHub project template is for IBM Hackathon projects. It includes pre-configured security files to help prevent accidental credential commits and potential account suspension during the hackathon.

## 🚀 Quick Start

1. **Use this template to create your project:**
   - Click "Use this template" button above and select "Create a new repository"
   - Name your repository
   - Click "Create repository"

2. **Clone your new repository:**

   ```bash
   git clone https://github.com/HACKATHON-ORG/your-repo-name.git
   cd your-repo-name
   ```

3. **Set up environment variables:**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your actual credentials
   # Use your preferred editor (nano, vim, code, etc.)
   nano .env
   ```

4. **Verify .gitignore is working:**

   ```bash
   # This should NOT show .env file
   git status

   # This should confirm .env is ignored
   git check-ignore -v .env
   ```

5. **Start developing!**

## 🔒 Security Features

This template includes:

- **`.gitignore`** - Prevents committing credentials and live session files
- **`.bobignore`** - Prevents AI assistants from logging credentials
- **`.env.example`** - Template for your environment variables

## 📋 Before Every Commit

Always run this checklist:

- [ ] Reviewed `git diff` for sensitive data
- [ ] No hardcoded API keys or passwords
- [ ] `.env` file is NOT in staged changes
- [ ] No files with "credential" or "secret" in name
- [ ] Used environment variables for all credentials

## 🆘 Need Help?

- Read [SECURITY.md](SECURITY.MD) for detailed guidelines
- Contact hackathon support through mentor channel
- Ask in the hackathon Slack workspace

---

**Remember:** Security is everyone's responsibility. When in doubt, ask for help!
