"""Pruebas unitarias del cliente HTTP del portal IBM API Connect.

Cubre: autenticación IAM (TC-001, TC-002), modo sin auth (TC-003),
SSL desactivado (TC-004), errores de configuración (TC-018, TC-019),
y opcionalidad de variables en tiempo de carga (TC-021, TC-022).
"""

from __future__ import annotations

import warnings
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Importar las funciones bajo prueba DESPUÉS de asegurarse de que el módulo
# puede cargarse sin variables de portal definidas (TC-021 / TC-022).
# ---------------------------------------------------------------------------
from smart_api_search.cli.ingest import build_portal_client, get_iam_token
from smart_api_search.config import Settings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _settings(**overrides: object) -> Settings:
    """Crea una instancia de Settings con valores de portal mínimos para test."""
    defaults: dict[str, object] = {
        "IBM_PORTAL_HOST": "https://portal.example.com",
        "IBM_PORTAL_AUTH": False,
        "IBM_PORTAL_VERIFY_SSL": True,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# TC-022 / AC-010: el módulo se importa sin variables del portal
# ---------------------------------------------------------------------------


def test_module_importable_without_portal_vars() -> None:
    """TC-022 — El módulo se importa sin error aunque falten variables del portal."""
    # El import al inicio del archivo ya es la prueba; si llegamos aquí, pasó.
    from smart_api_search.cli import ingest  # noqa: F401

    assert ingest is not None


# ---------------------------------------------------------------------------
# TC-001 / AC-001: autenticación IAM obtiene token y lo adjunta
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_iam_token_returns_access_token() -> None:
    """TC-001 — Con IBM_PORTAL_AUTH=true obtiene el token de la URL IAM."""
    settings = _settings(
        IBM_PORTAL_AUTH=True,
        IBM_TOKEN_URL="https://iam.example.com",
        IBM_INSTANCE_ID="inst-001",
        IBM_API_KEY="valid-api-key",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"access_token": "eyJhbGciOiJSUzI1NiJ9.test"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    token = await get_iam_token(settings, mock_client)

    assert token == "eyJhbGciOiJSUzI1NiJ9.test"
    mock_client.post.assert_awaited_once_with(
        "https://iam.example.com/inst-001/apikeys/token",
        json={"apikey": "valid-api-key"},
    )


@pytest.mark.asyncio
async def test_build_portal_client_with_auth_includes_authorization_header() -> None:
    """TC-001 — El cliente construido con auth incluye cabecera Authorization."""
    settings = _settings(
        IBM_PORTAL_AUTH=True,
        IBM_TOKEN_URL="https://iam.example.com",
        IBM_INSTANCE_ID="inst-001",
        IBM_API_KEY="valid-api-key",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"access_token": "my-token"}

    with patch("smart_api_search.cli.ingest.httpx.AsyncClient") as mock_cls:
        # Primera instancia temporal para obtener el token
        temp_client = AsyncMock()
        temp_client.post.return_value = mock_response
        temp_client.__aenter__ = AsyncMock(return_value=temp_client)
        temp_client.__aexit__ = AsyncMock(return_value=None)
        mock_cls.return_value = temp_client

        client = await build_portal_client(settings)

    # Verificar que se construyó el cliente final con la cabecera correcta
    assert client is not None
    # La segunda llamada a AsyncClient debe incluir headers con Authorization
    calls = mock_cls.call_args_list
    final_call_kwargs = calls[-1].kwargs
    assert "headers" in final_call_kwargs
    assert final_call_kwargs["headers"]["Authorization"] == "bearer my-token"


# ---------------------------------------------------------------------------
# TC-002 / AC-001: error cuando la respuesta IAM no contiene access_token
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_iam_token_raises_on_missing_access_token() -> None:
    """TC-002 — Error claro si la respuesta IAM no contiene access_token."""
    settings = _settings(
        IBM_PORTAL_AUTH=True,
        IBM_TOKEN_URL="https://iam.example.com",
        IBM_INSTANCE_ID="inst-001",
        IBM_API_KEY="valid-api-key",
    )

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {}  # Sin access_token

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with pytest.raises(SystemExit, match="1"):
        await get_iam_token(settings, mock_client)


# ---------------------------------------------------------------------------
# TC-003 / AC-002: modo sin autenticación — sin token, sin cabecera
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_portal_client_without_auth_has_no_authorization_header() -> None:
    """TC-003 — Sin auth no solicita token ni incluye cabecera Authorization."""
    settings = _settings(IBM_PORTAL_AUTH=False)

    with patch("smart_api_search.cli.ingest.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value = MagicMock()
        client = await build_portal_client(settings)

    assert client is not None
    calls = mock_cls.call_args_list
    final_call_kwargs = calls[-1].kwargs
    headers = final_call_kwargs.get("headers", {})
    assert "Authorization" not in headers


@pytest.mark.asyncio
async def test_build_portal_client_without_auth_does_not_call_iam() -> None:
    """TC-003 — Sin auth no se invoca get_iam_token."""
    settings = _settings(IBM_PORTAL_AUTH=False)

    with patch("smart_api_search.cli.ingest.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value = MagicMock()
        with patch("smart_api_search.cli.ingest.get_iam_token") as mock_token:
            await build_portal_client(settings)
            mock_token.assert_not_called()


# ---------------------------------------------------------------------------
# TC-004 / AC-003: SSL desactivado — verify=False y sin avisos
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_portal_client_ssl_disabled_uses_verify_false() -> None:
    """TC-004 — Con IBM_PORTAL_VERIFY_SSL=false el cliente usa verify=False."""
    settings = _settings(IBM_PORTAL_AUTH=False, IBM_PORTAL_VERIFY_SSL=False)

    with patch("smart_api_search.cli.ingest.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value = MagicMock()
        await build_portal_client(settings)

    calls = mock_cls.call_args_list
    final_kwargs = calls[-1].kwargs
    assert final_kwargs.get("verify") is False


@pytest.mark.asyncio
async def test_build_portal_client_ssl_disabled_suppresses_warnings() -> None:
    """TC-004 — Con IBM_PORTAL_VERIFY_SSL=false no se emiten warnings de SSL."""
    settings = _settings(IBM_PORTAL_AUTH=False, IBM_PORTAL_VERIFY_SSL=False)

    with patch("smart_api_search.cli.ingest.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value = MagicMock()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            await build_portal_client(settings)

    ssl_warnings = [
        w for w in caught if issubclass(w.category, Warning) and "ssl" in str(w.message).lower()
    ]
    assert ssl_warnings == []


# ---------------------------------------------------------------------------
# TC-018 / AC-009: error ante IBM_PORTAL_HOST ausente
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_portal_client_raises_on_missing_portal_host() -> None:
    """TC-018 — Falla con mensaje claro si IBM_PORTAL_HOST está ausente."""
    settings = _settings(IBM_PORTAL_HOST=None)  # type: ignore[arg-type]

    with pytest.raises(SystemExit, match="1"):
        await build_portal_client(settings)


# ---------------------------------------------------------------------------
# TC-019 / AC-009: error ante IBM_API_KEY ausente con auth activa
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_build_portal_client_raises_on_missing_api_key_with_auth() -> None:
    """TC-019 — Falla con mensaje claro si IBM_API_KEY falta con IBM_PORTAL_AUTH=true."""
    settings = _settings(
        IBM_PORTAL_AUTH=True,
        IBM_TOKEN_URL="https://iam.example.com",
        IBM_INSTANCE_ID="inst-001",
        IBM_API_KEY=None,  # type: ignore[arg-type]
    )

    with pytest.raises(SystemExit, match="1"):
        await build_portal_client(settings)


# ---------------------------------------------------------------------------
# TC-021 / AC-010: opcionalidad — Settings cargable sin variables del portal
# ---------------------------------------------------------------------------


def test_settings_instantiable_without_portal_vars() -> None:
    """TC-021 — Settings se puede instanciar sin ninguna variable del portal."""
    s = Settings()  # Sin IBM_PORTAL_HOST ni otras vars del portal
    assert s.IBM_PORTAL_AUTH is False
    assert s.IBM_PORTAL_VERIFY_SSL is True
    assert s.IBM_PORTAL_HOST is None
