"""Prueba de smoke: verifica que el paquete se importa correctamente
y que la enumeración de proveedores de embeddings está disponible.

Este test no llama a ningún servicio externo — es la verificación mínima
de que el scaffold del proyecto está operativo.
"""

import smart_api_search
from smart_api_search.config import EmbedProvider


def test_package_importable() -> None:
    """El paquete smart_api_search debe poderse importar."""
    assert smart_api_search.__name__ == "smart_api_search"


def test_embed_provider_values() -> None:
    """EmbedProvider debe exponer los dos proveedores configurados."""
    assert EmbedProvider.OPENAI == "openai"
    assert EmbedProvider.WATSONX == "watsonx"
    assert set(EmbedProvider) == {EmbedProvider.OPENAI, EmbedProvider.WATSONX}
