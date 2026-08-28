"""Módulo de configuración: carga variables de entorno con validación por contexto."""
from __future__ import annotations

from enum import StrEnum

from dotenv import load_dotenv

load_dotenv()


class EmbedProvider(StrEnum):
    OPENAI = "openai"
    WATSONX = "watsonx"
