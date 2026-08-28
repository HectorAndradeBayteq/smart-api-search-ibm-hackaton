# TK-002: Descubrimiento paginado y descarga de specs OpenAPI

**Estado:** Ready
**Historia:** [US-001](./README.md)
**Repositorio:** smart-api-search-ibm-hackaton

## Descripción

Implementar la fase de descubrimiento del portal IBM API Connect dentro de `src/smart_api_search/cli/ingest.py`: listar todas las APIs disponibles mediante paginación `GET /apis?page=N` hasta agotar el total indicado por el campo `count`; obtener los detalles de cada API con `GET /apis/{id}` en paralelo limitando la concurrencia a 12 peticiones simultáneas y conservando el orden de llegada; y descargar el attachment OpenAPI completo en formato JSON o YAML tolerando BOM al inicio. El fallo al obtener el detalle de una API individual no debe abortar el descubrimiento del resto.

## Dependencias

- `TK-001-cliente-portal-autenticacion` — cliente `httpx.AsyncClient` configurado con cabecera IAM, verificación SSL y `IBM_PORTAL_HOST`; debe estar disponible antes de ejecutar esta tarea
- `httpx==0.28.1` — cliente HTTP asíncrono para las llamadas al portal
- `asyncio.Semaphore` — control de concurrencia para las peticiones paralelas

## Referencias

- **Arquitectura:** no hay ADR específico para la estrategia de paginación o concurrencia; las decisiones aplicables se encuentran en el flujo FL-01 del technical-doc
- **Documentación técnica:** [docs/specs/technical-docs/smart-api-search.md#fl-01](../../technical-docs/smart-api-search.md#fl-01) — pasos 3 y tabla de manejo de errores (paso 3) del flujo de ingesta; describe paginación, paralelismo y descarga de attachment

## Archivos afectados

```text
smart-api-search-ibm-hackaton/
└── src/smart_api_search/
    ├── ~ cli/ingest.py                          # Funciones de descubrimiento paginado, descarga paralela y attachment
    └── ~ cli/__init__.py                        # Exportar nuevas funciones si es necesario
tests/
    └── + test_portal_discovery.py               # Pruebas unitarias con mocks del portal (paginación, semáforo, BOM, fallo parcial)
```

## Plan de implementación

- [ ] **IT-01** — Implementar función `list_all_apis(client) -> list[dict]` que itera `GET /apis?page=N` mientras haya páginas, usando el campo `count` de la primera respuesta para calcular el número total de páginas
  Retorna la lista completa de objetos API; lanza error claro si la respuesta no contiene `count`; no hace recursión, itera con bucle `while`
- [ ] **IT-02** — Implementar función `fetch_api_details(client, api_ids, max_concurrent=12) -> list[dict | None]` que descarga `GET /apis/{id}` en paralelo con `asyncio.Semaphore(12)`, conservando el orden de la lista de entrada
  El fallo de una petición individual produce `None` en esa posición y registra una advertencia (`logging.warning`), sin propagar la excepción; al finalizar, el llamador filtra los `None`
- [ ] **IT-03** — Implementar función `download_attachment(client, api_detail) -> tuple[bytes, str]` que extrae la URL del attachment OpenAPI del detalle de la API y descarga el contenido crudo
  Devuelve `(contenido_bytes, formato)` donde `formato` es `"json"` o `"yaml"` inferido de la extensión o cabecera `Content-Type`; lanza error claro con mensaje sin traza técnica si el detalle no contiene attachment
- [ ] **IT-04** — Implementar la eliminación del BOM (`\ufeff`) al inicio del contenido descargado antes de pasarlo al parser
  Aplicar tanto en modo texto (decodificado) como en modo bytes: `content.lstrip(b'\xef\xbb\xbf')` para bytes, `text.lstrip('\ufeff')` para str; nunca intentar reconstruir el spec desde `resources[]`
- [ ] **IT-05** — Integrar `list_all_apis`, `fetch_api_details` y `download_attachment` en el flujo principal de `ingest.py` para el modo `--source portal`
  Conectar con el cliente de TK-001; pasar los resultados hacia las funciones de parsing (TK-003); respetar `--dry-run` (preparar sin escribir ni descargar attachments)
- [ ] **IT-06** — Escribir pruebas unitarias en `tests/test_portal_discovery.py` con mocks de `httpx.AsyncClient`
  Cubrir: paginación correcta con varias páginas, paginación con una sola página, fallo de detalle individual sin abortar el resto, descarga de attachment JSON, descarga de attachment YAML con BOM, ausencia de attachment (error claro)

## Observaciones

- Los valores exactos de timeout y reintentos para las llamadas HTTP no están fijados en la especificación técnica (ver observación en `technical-docs/smart-api-search.md`); se puede iniciar con el timeout por defecto de `httpx` y registrar un pendiente de configuración.
- La estructura exacta del campo `attachment` dentro del objeto detalle de la API (`GET /apis/{id}`) no está documentada; deberá inspeccionarse contra el portal real o con un mock de la respuesta de ejemplo durante la implementación.
