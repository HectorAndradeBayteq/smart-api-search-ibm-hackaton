"""CLI de ingesta: indexa APIs desde el portal IBM o desde archivos locales."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import warnings
from typing import TYPE_CHECKING, cast

import httpx
import yaml

if TYPE_CHECKING:
    from smart_api_search.config import Settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TK-001: Cliente HTTP del portal y autenticación IAM
# ---------------------------------------------------------------------------


async def get_iam_token(settings: Settings, client: httpx.AsyncClient) -> str:
    """Obtiene el token de acceso IAM para el portal IBM API Connect.

    Realiza POST {IBM_TOKEN_URL}/{IBM_INSTANCE_ID}/apikeys/token con el
    cuerpo {"apikey": IBM_API_KEY} y devuelve el access_token de la respuesta.

    Solo debe invocarse cuando IBM_PORTAL_AUTH=True.

    Args:
        settings: Configuración del sistema con las variables IAM.
        client: Cliente HTTP asíncrono ya configurado para hacer la petición.

    Returns:
        El token de acceso como cadena de texto.

    Raises:
        SystemExit: Si la respuesta no contiene access_token o la petición falla.
    """
    url = f"{settings.IBM_TOKEN_URL}/{settings.IBM_INSTANCE_ID}/apikeys/token"
    try:
        response = await client.post(url, json={"apikey": settings.IBM_API_KEY})
        response.raise_for_status()
        data: dict[str, object] = response.json()
    except httpx.HTTPError as exc:
        print(f"Error: no se pudo obtener el token IAM: {exc}", file=sys.stderr)
        sys.exit(1)

    token = data.get("access_token")
    if not token:
        print("Error: la respuesta IAM no contiene 'access_token'.", file=sys.stderr)
        sys.exit(1)

    return str(token)


async def build_portal_client(settings: Settings) -> httpx.AsyncClient:
    """Construye un httpx.AsyncClient preconfigurado para el portal IBM.

    Valida que IBM_PORTAL_HOST esté presente. Si IBM_PORTAL_AUTH=True,
    obtiene el token IAM y adjunta la cabecera Authorization. Si
    IBM_PORTAL_VERIFY_SSL=False, desactiva la verificación de certificados
    y silencia los avisos de urllib3/httpx relacionados.

    Args:
        settings: Configuración del sistema con las variables de portal.

    Returns:
        AsyncClient configurado con base_url, headers y verify según los settings.

    Raises:
        SystemExit: Si falta IBM_PORTAL_HOST, o si IBM_PORTAL_AUTH=True y
            falta IBM_API_KEY.
    """
    # --- Validación de configuración (AC-009) ---
    if not settings.IBM_PORTAL_HOST:
        print("Error: falta la variable de entorno requerida: IBM_PORTAL_HOST.", file=sys.stderr)
        sys.exit(1)

    if settings.IBM_PORTAL_AUTH and not settings.IBM_API_KEY:
        print(
            "Error: falta la variable de entorno requerida: IBM_API_KEY"
            " (IBM_PORTAL_AUTH=true está activo).",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- SSL (AC-003) ---
    verify: bool | str = True
    if not settings.IBM_PORTAL_VERIFY_SSL:
        verify = False
        warnings.filterwarnings("ignore", message=".*SSL.*")
        warnings.filterwarnings("ignore", message=".*ssl.*")
        warnings.filterwarnings("ignore", message=".*certificate.*")
        warnings.filterwarnings("ignore", message=".*InsecureRequest.*")

    headers: dict[str, str] = {}

    # --- Autenticación IAM (AC-001 / AC-002) ---
    if settings.IBM_PORTAL_AUTH:
        async with httpx.AsyncClient() as temp_client:
            token = await get_iam_token(settings, temp_client)
        headers["Authorization"] = f"bearer {token}"

    return httpx.AsyncClient(
        base_url=settings.IBM_PORTAL_HOST,
        headers=headers,
        verify=verify,
    )


# ---------------------------------------------------------------------------
# TK-002: Descubrimiento paginado y descarga de specs OpenAPI
# ---------------------------------------------------------------------------


async def list_all_apis(client: httpx.AsyncClient) -> list[dict[str, object]]:
    """Lista todas las APIs del portal usando paginación GET /apis?page=N.

    Itera las páginas hasta haber acumulado el total indicado por el campo
    `count` de la primera respuesta. Utiliza un bucle while; no recursa.

    Args:
        client: Cliente HTTP configurado con base_url del portal.

    Returns:
        Lista completa de objetos API devueltos por el portal.

    Raises:
        SystemExit: Si la respuesta no contiene el campo 'count'.
    """
    all_apis: list[dict[str, object]] = []
    page = 1

    while True:
        response = await client.get("/apis", params={"page": page})
        response.raise_for_status()
        data: dict[str, object] = response.json()

        if "count" not in data:
            print("Error: la respuesta del portal no contiene el campo 'count'.", file=sys.stderr)
            sys.exit(1)

        total: int = int(cast(int, data["count"]))
        results: list[dict[str, object]] = cast(list[dict[str, object]], data.get("results", []))
        all_apis.extend(results)

        if total == 0 or len(all_apis) >= total:
            break

        page += 1

    return all_apis


async def fetch_api_details(
    client: httpx.AsyncClient,
    api_ids: list[str],
    max_concurrent: int = 12,
) -> list[dict[str, object] | None]:
    """Descarga detalles de APIs en paralelo con límite de concurrencia.

    Usa asyncio.Semaphore para limitar las peticiones en vuelo simultáneo.
    El fallo de una petición individual produce None en esa posición y registra
    una advertencia; no propaga la excepción ni aborta el resto.

    Args:
        client: Cliente HTTP configurado con base_url del portal.
        api_ids: Lista de IDs de APIs cuyos detalles descargar.
        max_concurrent: Número máximo de peticiones en vuelo simultáneo.

    Returns:
        Lista de detalles de API en el mismo orden que api_ids; None donde falló.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(api_id: str) -> dict[str, object] | None:
        async with semaphore:
            try:
                response = await client.get(f"/apis/{api_id}")
                response.raise_for_status()
                result: dict[str, object] = response.json()
                return result
            except (httpx.HTTPError, httpx.HTTPStatusError) as exc:
                logger.warning("No se pudo obtener el detalle de la API %s: %s", api_id, exc)
                return None

    tasks = [asyncio.create_task(fetch_one(api_id)) for api_id in api_ids]
    return list(await asyncio.gather(*tasks))


async def download_attachment(
    client: httpx.AsyncClient,
    api_detail: dict[str, object],
) -> tuple[bytes, str]:
    """Descarga el attachment OpenAPI de una API del portal.

    Extrae la URL del primer attachment del campo 'attachments' del detalle
    de la API. Descarga el contenido crudo y elimina el BOM UTF-8 si está
    presente. El formato se infiere de la URL o de la cabecera Content-Type.

    Args:
        client: Cliente HTTP configurado con base_url del portal.
        api_detail: Objeto detalle de la API, debe contener 'attachments'.

    Returns:
        Tupla (contenido_bytes_sin_bom, formato) donde formato es 'json' o 'yaml'.

    Raises:
        ValueError: Si el detalle no tiene attachment OpenAPI.
    """
    api_id = str(api_detail.get("id", "desconocida"))
    attachments: list[dict[str, object]] = cast(
        list[dict[str, object]], api_detail.get("attachments", [])
    )

    if not attachments:
        raise ValueError(
            f"La API '{api_id}' no tiene attachment OpenAPI. "
            "No se reconstruye el spec desde resources[]."
        )

    attachment = attachments[0]
    url = str(attachment.get("url", ""))

    response = await client.get(url)
    response.raise_for_status()

    content: bytes = response.content

    # --- Eliminar BOM UTF-8 (AC-008) ---
    bom = b"\xef\xbb\xbf"
    if content.startswith(bom):
        content = content[len(bom) :]

    # --- Inferir formato ---
    fmt = "json"
    content_type: str = str(response.headers.get("content-type", "")).lower()
    url_lower = url.lower()
    if "yaml" in content_type or url_lower.endswith(".yaml") or url_lower.endswith(".yml"):
        fmt = "yaml"

    return content, fmt


# ---------------------------------------------------------------------------
# TK-003: Procesamiento de fuentes, deeplinks y manejo de errores
# ---------------------------------------------------------------------------


def assign_source_name(slug: str, seen: set[str]) -> str:
    """Asigna un source_name estable y único con formato portal:{slug}.

    Si el nombre base ya existe en `seen`, añade sufijo numérico incremental
    desde -2 hasta encontrar un nombre libre. Actualiza `seen` antes de retornar.

    Args:
        slug: Identificador de la API en el portal (campo name u equivalente).
        seen: Conjunto de source_names ya asignados en esta ejecución; se
            modifica in-place añadiendo el nombre devuelto.

    Returns:
        Source_name único con formato ``portal:{slug}`` o ``portal:{slug}-N``.
    """
    base = f"portal:{slug}"
    candidate = base
    counter = 2
    while candidate in seen:
        candidate = f"{base}-{counter}"
        counter += 1
    seen.add(candidate)
    return candidate


def build_deeplink_map(
    api_detail: dict[str, object],
) -> dict[tuple[str, str], str]:
    """Construye el mapa de deeplinks (path, MÉTODO) → URL para una API.

    Recorre la sección ``resources`` del detalle de la API. Para cada recurso
    con ``path``, ``method`` y ``url``, añade la entrada al mapa con la clave
    ``(path, MÉTODO)`` en mayúsculas. Si el detalle no contiene ``resources``,
    devuelve un diccionario vacío (no lanza excepción).

    Para consultar un par ausente, usar ``.get((path, método), "")``.

    Args:
        api_detail: Objeto detalle de la API tal como lo devuelve el portal.

    Returns:
        Diccionario ``{(path, MÉTODO): url_deeplink}`` donde los métodos son
        siempre mayúsculas. Los pares sin recurso asociado no aparecen en el
        mapa; el llamador debe tratar las claves ausentes como cadena vacía.
    """
    resources = cast(list[dict[str, object]], api_detail.get("resources", []))
    deeplink_map: dict[tuple[str, str], str] = {}
    for resource in resources:
        path = str(resource.get("path", ""))
        method = str(resource.get("method", "")).upper()
        url = str(resource.get("url", ""))
        if path and method:
            deeplink_map[(path, method)] = url
    return deeplink_map


def process_portal_apis_attachments_errors(
    apis_details: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Clasifica los detalles de APIs según si tienen attachment OpenAPI.

    Itera los detalles; las APIs sin attachments se registran con logging.error
    (mensaje claro, sin traza técnica) y se acumulan en la lista de errores.
    Las que sí tienen attachments se acumulan en la lista de éxitos.
    No aborta el proceso ante fallos individuales (AC-005, AC-009).

    Args:
        apis_details: Lista de objetos detalle de API devueltos por el portal.

    Returns:
        Tupla ``(successes, errors)`` donde cada elemento es una lista de
        detalles de API. ``errors`` contiene las APIs sin attachment; el
        llamador decide si continúa o no con las demás operaciones.
    """
    successes: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for detail in apis_details:
        api_id = str(detail.get("id", "desconocida"))
        attachments = detail.get("attachments", [])
        if not attachments:
            logger.error(
                "La API '%s' no tiene attachment OpenAPI; se omite del procesamiento.",
                api_id,
            )
            errors.append(detail)
        else:
            successes.append(detail)
    return successes, errors


# ---------------------------------------------------------------------------
# TK-001 US-002: Parser de operaciones OpenAPI
# ---------------------------------------------------------------------------

#: Métodos HTTP estándar reconocidos por el parser (en minúsculas para comparación)
_HTTP_METHODS: frozenset[str] = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"}
)


def parse_spec(content: bytes, fmt: str) -> dict[str, object]:
    """Parsea el contenido crudo de un spec OpenAPI y devuelve el dict resultante.

    Tolera BOM UTF-8 al inicio del contenido. Soporta los formatos ``json`` y
    ``yaml``. Lanza ``ValueError`` con mensaje descriptivo si el formato no es
    reconocible o el parseo falla.

    Args:
        content: Bytes del spec (puede comenzar con BOM UTF-8).
        fmt: Formato del contenido. Valores válidos: ``"json"`` o ``"yaml"``.

    Returns:
        El spec como diccionario Python.

    Raises:
        ValueError: Si ``fmt`` no es ``"json"`` ni ``"yaml"``, o si el parseo falla.
    """
    bom = b"\xef\xbb\xbf"
    if content.startswith(bom):
        content = content[len(bom) :]

    text = content.decode("utf-8", errors="replace")

    if fmt == "json":
        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Error al parsear json: {exc}") from exc
        return dict(cast(dict[str, object], result))
    elif fmt == "yaml":
        try:
            result = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Error al parsear yaml: {exc}") from exc
        if not isinstance(result, dict):
            raise ValueError(f"El contenido yaml no es un mapping: {type(result)}")
        return cast(dict[str, object], result)
    else:
        raise ValueError(f"Formato no reconocido: '{fmt}'. Se esperaba 'json' o 'yaml'.")


def detect_spec_version(spec: dict[str, object]) -> str:
    """Detecta la versión del spec OpenAPI.

    Devuelve ``"oas3"`` si el spec contiene el campo ``openapi``, o
    ``"swagger2"`` si contiene el campo ``swagger``. Lanza ``ValueError``
    si ninguno está presente.

    Args:
        spec: Spec OpenAPI/Swagger ya parseado como diccionario.

    Returns:
        ``"oas3"`` o ``"swagger2"``.

    Raises:
        ValueError: Si el spec no tiene campo ``openapi`` ni ``swagger``.
    """
    if "openapi" in spec:
        return "oas3"
    if "swagger" in spec:
        return "swagger2"
    raise ValueError(
        "No se pudo determinar la versión del spec: no contiene campo 'openapi' ni 'swagger'."
    )


def get_base_url(spec: dict[str, object], version: str) -> str:
    """Extrae la URL base del servidor del spec.

    Para OAS3 usa ``servers[0].url`` si existe. Para Swagger 2.0 compone
    ``"{schemes[0]}://{host}{basePath}"`` con los campos disponibles; si alguno
    falta usa cadena vacía para ese segmento.

    Args:
        spec: Spec OpenAPI/Swagger ya parseado como diccionario.
        version: Versión detectada; ``"oas3"`` o ``"swagger2"``.

    Returns:
        URL base como cadena. Cadena vacía si no se pueden extraer datos.
    """
    if version == "oas3":
        servers = cast(list[dict[str, object]], spec.get("servers", []))
        if servers:
            return str(servers[0].get("url", ""))
        return ""

    # Swagger 2.0
    schemes = cast(list[str], spec.get("schemes", []))
    scheme = schemes[0] if schemes else ""
    host = str(spec.get("host", ""))
    base_path = str(spec.get("basePath", ""))

    if not host:
        return ""

    base = f"{scheme}://{host}" if scheme else host

    return f"{base}{base_path}"


def apply_text_fallback(operation: dict[str, object]) -> str:
    """Obtiene texto útil de una operación aplicando la cadena de respaldo.

    Orden de preferencia: ``summary`` → primera línea de ``description`` →
    ``operationId`` → concatenación de ``description`` de parámetros
    (separados por ``", "``). Devuelve cadena vacía si ninguna alternativa
    produce texto no vacío.

    Args:
        operation: Objeto operación del spec OpenAPI (sin modificar).

    Returns:
        Texto de respaldo como cadena. Nunca ``None``; puede ser vacío.
    """
    summary = str(operation.get("summary", "")).strip()
    if summary:
        return summary

    description = str(operation.get("description", "")).strip()
    if description:
        return description.splitlines()[0].strip()

    operation_id = str(operation.get("operationId", "")).strip()
    if operation_id:
        return operation_id

    params = cast(list[dict[str, object]], operation.get("parameters", []))
    param_descs = [
        str(p.get("description", "")).strip()
        for p in params
        if str(p.get("description", "")).strip()
    ]
    if param_descs:
        return ", ".join(param_descs)

    return ""


def build_raw_spec(
    spec: dict[str, object],
    path: str,
    method: str,
    fmt: str,
    version: str,
) -> dict[str, object]:
    """Construye el fragmento crudo MD-02 de una operación OpenAPI.

    Campos del fragmento: ``info``, ``servers`` (lista OAS3 o lista con
    objeto compuesto Swagger 2), ``format``, ``path``, ``method``
    (mayúsculas) y ``operation`` (objeto operation sin modificar).

    Args:
        spec: Spec completo como diccionario.
        path: Path de la operación (p. ej. ``"/users"``).
        method: Método HTTP en mayúsculas (p. ej. ``"GET"``).
        fmt: Formato del spec original (``"json"`` o ``"yaml"``).
        version: Versión del spec (``"oas3"`` o ``"swagger2"``).

    Returns:
        Diccionario con los seis campos de MD-02.
    """
    info = cast(dict[str, object], spec.get("info", {}))

    if version == "oas3":
        servers: list[dict[str, object]] = cast(list[dict[str, object]], spec.get("servers", []))
    else:
        # Swagger 2.0: construir objeto servidor compuesto
        schemes = cast(list[str], spec.get("schemes", []))
        servers = [
            {
                "url": get_base_url(spec, "swagger2"),
                "schemes": schemes,
                "host": str(spec.get("host", "")),
                "basePath": str(spec.get("basePath", "")),
            }
        ]

    paths_obj = cast(dict[str, dict[str, object]], spec.get("paths", {}))
    path_item = paths_obj.get(path, {})
    operation = cast(dict[str, object], path_item.get(method.lower(), {}))

    return {
        "info": info,
        "servers": servers,
        "format": fmt,
        "path": path,
        "method": method,
        "operation": operation,
    }


def extract_operations(
    spec: dict[str, object],
    source_file: str,
    fmt: str,
) -> list[dict[str, object]]:
    """Extrae todas las operaciones OpenAPI de la sección ``paths`` del spec.

    Para cada operación: normaliza el método HTTP a mayúsculas; aplica la
    cadena de respaldo de texto (``apply_text_fallback``); construye el
    fragmento crudo MD-02 (``build_raw_spec``); compone el dict parcial de
    QdrantPoint con los campos requeridos por MD-01.

    Sólo procesa métodos HTTP estándar (GET, POST, PUT, DELETE, PATCH, HEAD,
    OPTIONS, TRACE). Las claves de path-item que no sean métodos HTTP estándar
    (p. ej. ``"parameters"``, ``"summary"``) se ignoran.

    Args:
        spec: Spec completo como diccionario.
        source_file: Identificador de la fuente (p. ej. ``"portal:my-api"``).
        fmt: Formato del spec original (``"json"`` o ``"yaml"``).

    Returns:
        Lista de dicts parciales de QdrantPoint, uno por operación encontrada.
    """
    version = detect_spec_version(spec)
    server_url = get_base_url(spec, version)
    info = cast(dict[str, object], spec.get("info", {}))
    api_title = str(info.get("title", ""))
    api_version = str(info.get("version", ""))
    api_description = str(info.get("description", ""))

    paths = cast(dict[str, dict[str, object]], spec.get("paths", {}))
    operations: list[dict[str, object]] = []

    for path, path_item in paths.items():
        for key, operation_obj in path_item.items():
            if key.lower() not in _HTTP_METHODS:
                continue

            method = key.upper()
            operation = cast(dict[str, object], operation_obj)

            summary = clean_text(apply_text_fallback(operation))
            description = clean_text(str(operation.get("description", "")))
            tags = cast(list[str], operation.get("tags", []))
            operation_id = str(operation.get("operationId", ""))

            raw_spec_dict = build_raw_spec(spec, path, method, fmt, version)
            raw_spec_json = json.dumps(raw_spec_dict)

            spec_ref = f"{source_file}|{method}|{path}"

            operations.append(
                {
                    "method": method,
                    "path": path,
                    "summary": summary,
                    "description": description,
                    "server_url": server_url,
                    "spec_format": fmt,
                    "source_file": source_file,
                    "spec_ref": spec_ref,
                    "raw_spec": raw_spec_json,
                    "tags": tags,
                    "operationId": operation_id,
                    "api_title": api_title,
                    "api_version": api_version,
                    "api_description": api_description,
                }
            )

    return operations


# ---------------------------------------------------------------------------
# TK-002 US-002: Limpieza de texto y documento marcador
# ---------------------------------------------------------------------------


def clean_text(text: str) -> str:
    """Limpia el texto de una operación OpenAPI eliminando marcado de documentación.

    Aplica en orden: (a) elimina macros de plantilla tipo Hugo/Jinja
    (``{{% … %}}``, ``{{< … >}}``, ``{{ … }}``); (b) elimina bloques de
    admonición RST (``.. note::``, ``.. warning::``, ``.. tip::``, etc.) y
    Markdown (``!!! note``, ``!!! warning``); (c) colapsa espacios internos
    múltiples (incluidas tabulaciones) en un solo espacio; (d) colapsa tres o
    más saltos de línea consecutivos en dos; (e) aplica ``strip()``.

    La función es pura (sin efectos secundarios) e idempotente:
    ``clean_text(clean_text(x)) == clean_text(x)``.

    Args:
        text: Texto original de la operación (puede contener markup).

    Returns:
        Texto limpio, sin macros ni admoniciones ni espacios redundantes.
    """
    if not text:
        return text

    # (a) Macros Hugo/Jinja: {{% ... %}},  {{< ... >}},  {{ ... }}
    result = re.sub(r"\{%[^%]*%\}", "", text)
    result = re.sub(r"\{\{<[^>]*>\}\}", "", result)
    result = re.sub(r"\{\{%[^%]*%\}\}", "", result)
    result = re.sub(r"\{\{[^}]*\}\}", "", result)

    # (b1) Admoniciones RST: líneas que comienzan con ".. <palabra>::"
    result = re.sub(r"^\.\. \w+::\s*$", "", result, flags=re.MULTILINE)

    # (b2) Admoniciones Markdown: líneas que comienzan con "!!! <palabra>"
    result = re.sub(r"^!!!\s+\w+.*$", "", result, flags=re.MULTILINE)

    # (c) Colapsar tabulaciones y espacios múltiples en un solo espacio
    #     (solo dentro de cada línea, sin cruzar saltos de línea)
    result = re.sub(r"[^\S\n]+", " ", result)

    # (d) Colapsar tres o más saltos de línea consecutivos en dos
    result = re.sub(r"\n{3,}", "\n\n", result)

    # (e) Strip
    return result.strip()


def make_marker_document(
    spec: dict[str, object],
    source_file: str,
    fmt: str,
) -> dict[str, object]:
    """Genera un documento marcador para specs OpenAPI sin sección ``paths``.

    Cuando un spec no declara ``paths`` (o lo declara vacío), este documento
    garantiza que la API no desaparezca en silencio del índice (AC-005). El
    marcador pasa por el mismo pipeline de indexación que una operación normal.

    Args:
        spec: Spec completo como diccionario (sin ``paths`` o con ``paths: {}``).
        source_file: Identificador de la fuente (p. ej. ``"portal:my-api"``).
        fmt: Formato del spec original (``"json"`` o ``"yaml"``).

    Returns:
        Dict parcial de QdrantPoint con todos los campos obligatorios del marcador.
    """
    info = cast(dict[str, object], spec.get("info", {}))
    api_title = str(info.get("title", ""))
    api_version = str(info.get("version", ""))
    api_description = str(info.get("description", ""))

    raw_spec_dict: dict[str, object] = {"info": info, "format": fmt}

    return {
        "source_file": source_file,
        "spec_format": fmt,
        "api_title": api_title,
        "api_version": api_version,
        "api_description": api_description,
        "method": "MARKER",
        "path": "/",
        "spec_ref": f"{source_file}|MARKER|/",
        "summary": "(no paths declared)",
        "raw_spec": json.dumps(raw_spec_dict),
    }


# ---------------------------------------------------------------------------
# TK-003 US-002: Configuración de metadatos por categoría
# ---------------------------------------------------------------------------


def load_category_config(path: str) -> dict[str, dict[str, str]]:
    """Carga y valida el archivo de configuración de categorías ``categories.yaml``.

    Si el archivo no existe lanza ``SystemExit(1)`` imprimiendo la ruta. Si
    tiene sintaxis YAML inválida lanza ``SystemExit(1)`` con la ruta y la
    causa. Un archivo vacío devuelve un dict vacío (sin fallar).

    Args:
        path: Ruta al archivo YAML de configuración de categorías.

    Returns:
        Dict ``{category_key: {title?, description?}}`` con los campos presentes.

    Raises:
        SystemExit: Si el archivo no existe o tiene sintaxis YAML inválida.
    """
    if not os.path.exists(path):
        print(
            f"Error: no se encontró el archivo de configuración de categorías: {path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(path, encoding="utf-8") as fh:
        raw = fh.read()

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        print(f"Error: sintaxis inválida en {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if data is None:
        return {}

    return cast(dict[str, dict[str, str]], data)


# ---------------------------------------------------------------------------
# TK-004 US-002: Aplicación de metadatos de presentación
# ---------------------------------------------------------------------------


def resolve_category_key(operation: dict[str, object]) -> str:
    """Determina la clave de categoría de una operación a partir de sus tags.

    Devuelve el primer elemento de ``operation["tags"]`` si la lista es no
    vacía y el primer tag no está en blanco. En cualquier otro caso devuelve
    cadena vacía ``""``; nunca lanza excepción.

    Args:
        operation: Dict parcial de QdrantPoint con campo ``tags``.

    Returns:
        Clave de categoría como cadena, o ``""`` si no hay tag válido.
    """
    tags = cast(list[str], operation.get("tags", []))
    if tags and str(tags[0]).strip():
        return str(tags[0]).strip()
    return ""


def apply_category_metadata(
    operation: dict[str, object],
    category_config: dict[str, dict[str, str]],
) -> dict[str, object]:
    """Enriquece la operación con el campo ``category`` según MD-04.

    Si la clave de categoría tiene entrada en ``category_config`` con ``title``
    o ``description``, usa esos valores. En caso contrario usa ``api_title``
    como ``category``. No muta el dict original.

    Args:
        operation: Dict parcial de QdrantPoint a enriquecer.
        category_config: Mapa ``{category_key: {title?, description?}}``
            cargado por ``load_category_config``.

    Returns:
        Nuevo dict con el campo ``category`` añadido.
    """
    key = resolve_category_key(operation)
    entry = category_config.get(key, {}) if key else {}

    if entry.get("title") or entry.get("description"):
        category = key
    else:
        category = str(operation.get("api_title", ""))

    return {**operation, "category": category}


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------


def main() -> None:
    """Punto de entrada de la CLI de ingesta."""
    raise NotImplementedError("CLI de ingesta no implementada aún")


if __name__ == "__main__":  # pragma: no cover
    main()
