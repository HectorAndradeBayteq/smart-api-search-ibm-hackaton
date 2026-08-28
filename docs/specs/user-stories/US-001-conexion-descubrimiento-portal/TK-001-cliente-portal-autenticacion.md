# TK-001: Cliente HTTP del portal y autenticación IAM

**Estado:** Ready
**Historia:** [US-001](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar el cliente HTTP configurado para el portal IBM API Connect dentro de `src/smart_api_search/cli/ingest.py`: leer las variables de entorno del portal (`IBM_PORTAL_HOST`, `IBM_PORTAL_AUTH`, `IBM_TOKEN_URL`, `IBM_INSTANCE_ID`, `IBM_API_KEY`, `IBM_PORTAL_VERIFY_SSL`) de forma opcional (ninguna variable del portal debe impedir arrancar el servidor en modo archivos ni ejecutar la suite de pruebas); obtener el token IAM con `POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token` y adjuntarlo como cabecera `Authorization: bearer <token>` cuando `IBM_PORTAL_AUTH=true`; no solicitar token ni enviar cabecera `Authorization` cuando `IBM_PORTAL_AUTH=false`; y desactivar la verificación SSL y silenciar los avisos de certificado no confiable cuando `IBM_PORTAL_VERIFY_SSL=false`.

## Dependencias

- `httpx==0.28.1` — cliente HTTP asíncrono para la obtención del token y las llamadas al portal
- `python-dotenv==1.2.3` — carga de variables de entorno desde `.env`
- `src/smart_api_search/config.py` — módulo de configuración existente; extender con las variables de portal si aún no están declaradas

## Referencias

- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#md-05](../../technical-docs/smart-api-search.md#md-05) — modelo MD-05 (Settings): campos `IBM_PORTAL_HOST`, `IBM_PORTAL_AUTH`, `IBM_TOKEN_URL`, `IBM_INSTANCE_ID`, `IBM_API_KEY`, `IBM_PORTAL_VERIFY_SSL` con sus restricciones
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — paso 3 del flujo FL-01: obtención del token IAM y construcción del cliente antes del descubrimiento paginado

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    ├── ~ config.py                              # Extender Settings con variables del portal (si no existen)
    └── ~ cli/ingest.py                          # Función build_portal_client(); obtención del token IAM
tests/
    └── + test_portal_client.py                  # Pruebas unitarias: con auth, sin auth, SSL desactivado, opcionalidad en modo archivos
```

## Plan de implementación

- [x] **IT-01** — Extender `config.py` con las variables del portal como campos opcionales en `Settings`: `IBM_PORTAL_HOST`, `IBM_PORTAL_AUTH` (bool, default `False`), `IBM_TOKEN_URL`, `IBM_INSTANCE_ID`, `IBM_API_KEY`, `IBM_PORTAL_VERIFY_SSL` (bool, default `True`)
  Ninguna de estas variables debe ser obligatoria a nivel de módulo; la validación de presencia se hace en el momento de uso (al construir el cliente), no en tiempo de carga
- [x] **IT-02** — Implementar función `get_iam_token(settings) -> str` que realiza `POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token` con cuerpo `{"apikey": IBM_API_KEY}` y devuelve el token de acceso de la respuesta
  Solo se invoca cuando `IBM_PORTAL_AUTH=True`; lanza error claro sin traza técnica si la petición falla o la respuesta no contiene el token
- [x] **IT-03** — Implementar función `build_portal_client(settings) -> httpx.AsyncClient` que construye y devuelve un `httpx.AsyncClient` preconfigurado
  Si `IBM_PORTAL_AUTH=True`: llama a `get_iam_token` e incluye `headers={"Authorization": f"bearer {token}"}`; si `IBM_PORTAL_AUTH=False`: no solicita token ni incluye cabecera `Authorization`; si `IBM_PORTAL_VERIFY_SSL=False`: `verify=False` + `warnings.filterwarnings("ignore", ...)` para silenciar avisos de `urllib3`/`httpx`; base URL fijada en `IBM_PORTAL_HOST`
- [x] **IT-04** — Garantizar opcionalidad en tiempo de carga: las variables del portal no deben evaluarse ni requerirse al importar el módulo; la validación de `IBM_PORTAL_HOST` y de `IBM_API_KEY` (cuando `IBM_PORTAL_AUTH=True`) ocurre únicamente al llamar a `build_portal_client`
  El arranque del servidor en modo archivos (`--source files`) y la ejecución de `pytest` sin variables del portal no deben producir error alguno
- [x] **IT-05** — Escribir pruebas unitarias en `tests/test_portal_client.py` con mocks de `httpx.AsyncClient`
  Cubrir: obtención de token con `IBM_PORTAL_AUTH=True` (cabecera presente), modo sin auth (sin cabecera ni petición de token), `IBM_PORTAL_VERIFY_SSL=False` (verify desactivado y sin avisos), ausencia de `IBM_PORTAL_HOST` al construir cliente (error claro), ausencia de variables de portal al importar (sin error)

## Observaciones

- Los valores exactos de timeout para la petición de token no están fijados en la especificación técnica (ver observación en `technical-docs/smart-api-search.md`); iniciar con el timeout por defecto de `httpx`.
- Si `Settings` ya tiene una clase base o un mecanismo de validación establecido en `config.py`, respetarlo al añadir los campos del portal.
