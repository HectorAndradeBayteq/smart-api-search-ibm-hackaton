"""Normalización de parámetros de operaciones OpenAPI.

Extrae los parámetros declarados en el objeto ``operation`` del payload y los
que se pueden inferir del template del path (``{param}`` en la ruta). Los
parámetros sin nombre se omiten (AC-006).
"""

from __future__ import annotations

import re
from typing import Any


def normalize_params(
    operation: dict[str, Any],
    path_template: str,
) -> list[dict[str, Any]]:
    """Normaliza parámetros de la operación combinándolos con los del path template.

    Extrae los parámetros del campo ``parameters`` del objeto ``operation``
    (declarados en el spec). A continuación infiere parámetros de path a partir
    de ``{param}`` en ``path_template`` que no estén ya declarados. Los
    parámetros sin nombre se omiten.

    Args:
        operation: Objeto ``operation`` del payload (campo ``raw_spec.operation``).
        path_template: Path de la operación, p. ej. ``/users/{userId}/posts/{postId}``.

    Returns:
        Lista de dicts con al menos ``name``, ``in`` y ``required`` por entrada.
    """
    result: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    # Parámetros declarados en la operación
    declared: list[Any] = operation.get("parameters") or []
    for param in declared:
        if not isinstance(param, dict):
            continue
        name: str = str(param.get("name") or "").strip()
        if not name:
            continue  # omitir parámetros sin nombre (AC-006)
        seen_names.add(name)
        result.append(
            {
                "name": name,
                "in": str(param.get("in") or "query"),
                "required": bool(param.get("required", False)),
                **{k: v for k, v in param.items() if k not in ("name", "in", "required")},
            }
        )

    # Parámetros inferidos del template del path
    for match in re.finditer(r"\{([^}]+)\}", path_template):
        param_name = match.group(1).strip()
        if not param_name or param_name in seen_names:
            continue
        result.append(
            {
                "name": param_name,
                "in": "path",
                "required": True,
            }
        )

    return result
