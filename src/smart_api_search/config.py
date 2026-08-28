"""Módulo de configuración: carga variables de entorno con validación por contexto."""
from __future__ import annotations

from enum import StrEnum

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class EmbedProvider(StrEnum):
    """Proveedores de embeddings soportados."""

    OPENAI = "openai"
    WATSONX = "watsonx"


class Settings(BaseSettings):
    """Configuración del sistema leída desde variables de entorno (MD-05).

    Todos los campos son opcionales en tiempo de carga; la validación de
    presencia ocurre en la capa que los necesita (portal, servidor MCP, etc.).
    """

    # --- Servidor MCP ---
    MCP_HOST: str = Field(default="127.0.0.1")
    MCP_PORT: int = Field(default=8000)
    MCP_PATH: str = Field(default="/mcp")

    # --- Portal IBM API Connect ---
    IBM_PORTAL_HOST: str | None = Field(default=None)
    IBM_PORTAL_AUTH: bool = Field(default=False)
    IBM_TOKEN_URL: str | None = Field(default=None)
    IBM_INSTANCE_ID: str | None = Field(default=None)
    IBM_API_KEY: str | None = Field(default=None)
    IBM_PORTAL_VERIFY_SSL: bool = Field(default=True)

    model_config = {"env_file": ".env", "extra": "ignore"}
