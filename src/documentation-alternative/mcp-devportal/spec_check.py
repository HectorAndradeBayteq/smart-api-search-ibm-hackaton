"""Puerta de calidad de documentacion para specs OpenAPI.

El Developer Portal no acepta cualquier spec: exige que cada operacion se
entienda en terminos de negocio. Este modulo implementa esa revision y es el
mismo criterio que el agente documentador debe satisfacer antes de publicar.
"""

from __future__ import annotations

HTTP_METHODS = ("get", "put", "post", "delete", "patch", "head", "options", "trace")

MIN_INFO_DESCRIPTION = 40
MIN_OP_DESCRIPTION = 30
DEFAULT_THRESHOLD = 80


def _operations(spec: dict):
    """Devuelve (ruta, metodo, operacion) por cada operacion del documento."""
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() in HTTP_METHODS and isinstance(op, dict):
                yield path, method.lower(), op


def _has_example(node: dict) -> bool:
    """True si un requestBody/response trae ejemplo en cualquier content-type."""
    for media in (node.get("content") or {}).values():
        if not isinstance(media, dict):
            continue
        if media.get("example") is not None or media.get("examples"):
            return True
        schema = media.get("schema") or {}
        if isinstance(schema, dict) and schema.get("example") is not None:
            return True
    return False


def check_spec(spec: dict, threshold: int = DEFAULT_THRESHOLD) -> dict:
    """Evalua la spec y devuelve puntaje, bloqueantes y advertencias."""
    blocking: list[str] = []
    warnings: list[str] = []

    if not spec.get("openapi", "").startswith("3."):
        blocking.append("info: se requiere OpenAPI 3.x (campo 'openapi').")

    info = spec.get("info") or {}
    if not info.get("title"):
        blocking.append("info.title: falta el titulo del API.")
    if not info.get("version"):
        blocking.append("info.version: falta la version del API.")

    info_desc = (info.get("description") or "").strip()
    if len(info_desc) < MIN_INFO_DESCRIPTION:
        blocking.append(
            f"info.description: falta una descripcion funcional del API "
            f"(minimo {MIN_INFO_DESCRIPTION} caracteres)."
        )

    if not info.get("contact"):
        warnings.append("info.contact: sin equipo responsable; el portal lo muestra como huerfano.")

    if not spec.get("servers"):
        warnings.append("servers: sin URL base declarada.")

    schemes = ((spec.get("components") or {}).get("securitySchemes")) or {}
    if not schemes:
        blocking.append("components.securitySchemes: no se declara como se autentica el API.")

    global_security = bool(spec.get("security"))

    ops = list(_operations(spec))
    if not ops:
        blocking.append("paths: el documento no contiene operaciones.")
        return {
            "score": 0,
            "operations": 0,
            "documented_operations": 0,
            "blocking": blocking,
            "warnings": warnings,
            "passed": False,
            "threshold": threshold,
        }

    seen_ids: set[str] = set()
    documented = 0

    for path, method, op in ops:
        label = f"{method.upper()} {path}"
        gaps: list[str] = []

        if not (op.get("summary") or "").strip():
            gaps.append("sin summary")

        if len((op.get("description") or "").strip()) < MIN_OP_DESCRIPTION:
            gaps.append("sin description funcional")

        op_id = (op.get("operationId") or "").strip()
        if not op_id:
            gaps.append("sin operationId")
        elif op_id in seen_ids:
            blocking.append(f"{label}: operationId '{op_id}' duplicado.")
        else:
            seen_ids.add(op_id)

        if not op.get("tags"):
            warnings.append(f"{label}: sin tags; el portal no puede agruparlo.")

        for param in op.get("parameters") or []:
            if isinstance(param, dict) and not (param.get("description") or "").strip():
                gaps.append(f"parametro '{param.get('name', '?')}' sin description")

        body = op.get("requestBody")
        if isinstance(body, dict):
            if not (body.get("description") or "").strip():
                gaps.append("requestBody sin description")
            if not _has_example(body):
                warnings.append(f"{label}: requestBody sin ejemplo.")

        responses = op.get("responses") or {}
        codes = [str(c) for c in responses]
        if not any(c.startswith("2") for c in codes):
            gaps.append("sin respuesta 2xx documentada")
        if not any(c.startswith("4") for c in codes):
            warnings.append(f"{label}: sin respuesta de error 4xx documentada.")

        for code, resp in responses.items():
            if isinstance(resp, dict) and not (resp.get("description") or "").strip():
                gaps.append(f"respuesta {code} sin description")

        if not any(_has_example(r) for r in responses.values() if isinstance(r, dict)):
            warnings.append(f"{label}: ninguna respuesta trae ejemplo.")

        if not op.get("security") and not global_security:
            gaps.append("sin requisito de seguridad declarado")

        if gaps:
            blocking.append(f"{label}: " + "; ".join(gaps) + ".")
        else:
            documented += 1

    score = round(documented * 100 / len(ops))

    return {
        "score": score,
        "operations": len(ops),
        "documented_operations": documented,
        "blocking": blocking,
        "warnings": warnings,
        "passed": not blocking and score >= threshold,
        "threshold": threshold,
    }


def format_report(result: dict) -> str:
    """Convierte el resultado en texto legible para el agente."""
    lines = [
        f"Cobertura de documentacion: {result['score']}% "
        f"({result['documented_operations']}/{result['operations']} operaciones completas) "
        f"· minimo requerido {result['threshold']}%",
        f"Resultado: {'APTA para publicar' if result['passed'] else 'NO apta para publicar'}",
    ]

    if result["blocking"]:
        lines.append("")
        lines.append(f"Bloqueantes ({len(result['blocking'])}):")
        lines += [f"  - {item}" for item in result["blocking"]]

    if result["warnings"]:
        lines.append("")
        lines.append(f"Advertencias ({len(result['warnings'])}):")
        lines += [f"  - {item}" for item in result["warnings"]]

    return "\n".join(lines)
