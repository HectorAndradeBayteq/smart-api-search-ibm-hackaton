"""Módulo de configuración: carga variables de entorno con validación por contexto."""
from __future__ import annotations

from enum import StrEnum

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class EmbedProvider(StrEnum):
    """Proveedores de embeddings soportados (AC-025)."""

    OPENAI = "openai"
    WATSONX = "watsonx"


class Settings(BaseSettings):
    """Configuración del sistema leída desde variables de entorno (MD-05).

    Todos los campos del portal son opcionales en tiempo de carga;
    la validación de presencia ocurre únicamente al construir el cliente
    de portal (AC-010). Las variables de Qdrant y embeddings son igualmente
    opcionales en carga; su presencia se valida al construir los clientes
    correspondientes.
    """

    # --- Servidor MCP ---
    MCP_HOST: str = Field(default="127.0.0.1")
    MCP_PORT: int = Field(default=8000)
    MCP_PATH: str = Field(default="/mcp")

    # --- Qdrant Cloud (ADR-002) ---
    QDRANT_URL: str | None = Field(default=None)
    QDRANT_API_KEY: str | None = Field(default=None)
    QDRANT_COLLECTION: str = Field(default="smart-api-search")
    COLLECTION_NAME: str = Field(default="api-operations")

    # --- Portal IBM API Connect ---
    IBM_PORTAL_HOST: str | None = Field(default=None)
    IBM_PORTAL_AUTH: bool = Field(default=False)
    IBM_TOKEN_URL: str | None = Field(default=None)
    IBM_INSTANCE_ID: str | None = Field(default=None)
    IBM_API_KEY: str | None = Field(default=None)
    IBM_PORTAL_VERIFY_SSL: bool = Field(default=True)

    # --- Fuente de archivos locales (AC-015) ---
    LOCAL_SPECS_DIR: str | None = Field(default=None)

    # --- Embeddings (ADR-009, ADR-014, AC-026, AC-027) ---
    # EMBED_DIM NUNCA debe aparecer como literal en el código; leer siempre de aquí.
    EMBED_DIM: int = Field(default=1024)
    EMBED_PROVIDER: EmbedProvider = Field(default=EmbedProvider.OPENAI)

    # --- Watsonx (ADR-014) ---
    WATSONX_API_KEY: str | None = Field(default=None)
    WATSONX_URL: str | None = Field(default=None)
    WATSONX_PROJECT_ID: str | None = Field(default=None)

    # --- OpenAI ---
    OPENAI_API_KEY: str | None = Field(default=None)

    # --- HyDE (ADR-008) ---
    HYDE_ENABLED: bool = Field(default=True)

    model_config = {"env_file": ".env", "extra": "ignore"}


# Instancia global de configuración para uso en módulos de producción.
# Los tests que necesiten controlar la configuración deben hacer patch de este objeto.
settings = Settings()
