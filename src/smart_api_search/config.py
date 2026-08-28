"""Módulo de configuración: carga variables de entorno con validación por contexto."""

from __future__ import annotations

from enum import StrEnum

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class EmbedProvider(StrEnum):
    OPENAI = "openai"
    WATSONX = "watsonx"


class Settings(BaseSettings):
    """Configuración del sistema leída desde variables de entorno.

    Todos los campos del portal son opcionales en tiempo de carga;
    la validación de presencia ocurre únicamente al construir el cliente
    de portal (AC-010).
    """

    # --- Portal IBM API Connect ---
    IBM_PORTAL_HOST: str | None = Field(default=None)
    IBM_PORTAL_AUTH: bool = Field(default=False)
    IBM_TOKEN_URL: str | None = Field(default=None)
    IBM_INSTANCE_ID: str | None = Field(default=None)
    IBM_API_KEY: str | None = Field(default=None)
    IBM_PORTAL_VERIFY_SSL: bool = Field(default=True)

    model_config = {"env_file": ".env", "extra": "ignore"}
