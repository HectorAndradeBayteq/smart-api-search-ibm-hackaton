"""Fuente de specs locales: descubrimiento recursivo y construcción de source_file.

Implementa ``discover_specs()`` y ``build_source_file()`` para el modo
``--source files`` de la CLI de ingesta (AC-015, AC-016, AC-017, BR-06).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml

#: Extensiones reconocidas como specs OpenAPI locales.
_SPEC_EXTENSIONS = {".json", ".yaml", ".yml"}


def discover_specs(specs_dir: str) -> list[Path]:
    """Descubre recursivamente los archivos spec en ``specs_dir``.

    Solo devuelve archivos con extensiones ``.json``, ``.yaml`` o ``.yml``.

    Args:
        specs_dir: Ruta al directorio (relativa o absoluta).

    Returns:
        Lista de ``Path`` a los archivos encontrados.
    """
    root = Path(specs_dir).resolve()
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in _SPEC_EXTENSIONS]


def build_source_file(abs_specs_dir: Path, abs_file: Path) -> str:
    """Construye el ``source_file`` para un archivo local.

    Ambas rutas se resuelven a absolutas antes de calcular la relativa
    (BR-06, AC-017). El resultado tiene formato ``file:{relativa}``.

    Args:
        abs_specs_dir: Directorio raíz de specs (ya absoluto o a resolver).
        abs_file: Ruta al archivo de spec (ya absoluta o a resolver).

    Returns:
        Cadena ``file:{ruta_relativa}`` donde la relativa es relativa a ``abs_specs_dir``.
    """
    base = abs_specs_dir.resolve()
    file_abs = abs_file.resolve()
    relative = file_abs.relative_to(base)
    return f"file:{relative.as_posix()}"


def load_spec_file(path: Path) -> tuple[dict[str, object], str]:
    """Carga un archivo spec con tolerancia a BOM (AC-019).

    Args:
        path: Ruta al archivo de spec.

    Returns:
        Tupla ``(spec_dict, formato)`` donde formato es ``"json"`` o ``"yaml"``.

    Raises:
        ValueError: Si el archivo no se puede parsear.
    """
    content = path.read_text(encoding="utf-8-sig")  # tolera BOM (AC-019)
    fmt = "json" if path.suffix == ".json" else "yaml"

    result = json.loads(content) if fmt == "json" else yaml.safe_load(content)

    if not isinstance(result, dict):
        raise ValueError(f"El archivo {path} no contiene un mapping válido.")

    return cast(dict[str, object], result), fmt
