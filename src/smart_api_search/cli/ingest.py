"""CLI de ingesta: indexa APIs desde el portal IBM o desde archivos locales."""

from __future__ import annotations

import asyncio
import logging
import sys
import warnings
from typing import TYPE_CHECKING, cast

import httpx

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
# Punto de entrada
# ---------------------------------------------------------------------------


def main() -> None:
    """Punto de entrada de la CLI de ingesta."""
    raise NotImplementedError("CLI de ingesta no implementada aún")


if __name__ == "__main__":  # pragma: no cover
    main()
