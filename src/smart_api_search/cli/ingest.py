"""CLI de ingesta: indexa APIs desde el portal IBM o desde archivos locales."""

from __future__ import annotations

import sys
import warnings
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from smart_api_search.config import Settings


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


def main() -> None:
    """Punto de entrada de la CLI de ingesta."""
    raise NotImplementedError("CLI de ingesta no implementada aún")


if __name__ == "__main__":  # pragma: no cover
    main()
