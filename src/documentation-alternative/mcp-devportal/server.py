#!/usr/bin/env python3
"""Servidor MCP 'devportal': publica documentacion de APIs en el Developer Portal.

Implementa el protocolo MCP (JSON-RPC 2.0 sobre stdio) usando solo la libreria
estandar de Python, para que la demo no dependa de instalar paquetes.

Herramientas expuestas:
  devportal_status        estado y modo de conexion del portal
  devportal_validate_spec puerta de calidad de documentacion (sin publicar)
  devportal_publish_api   valida y publica una spec OpenAPI en el portal
  devportal_list_apis     lista lo publicado en el catalogo
  devportal_get_api       recupera una spec publicada (verificacion)
  devportal_unpublish_api retira una publicacion (limpieza de la demo)

Uso manual (fuera de un cliente MCP):
  echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python server.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spec_check  # noqa: E402
from portal import Portal, PortalError  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "devportal", "version": "1.0.0"}

TOOLS = [
    {
        "name": "devportal_status",
        "description": (
            "Muestra contra que Developer Portal se va a publicar (modo mock, apic o generic), "
            "el catalogo destino y si hay credenciales. Usar antes de publicar para confirmar el destino."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "devportal_validate_spec",
        "description": (
            "Revisa si una spec OpenAPI cumple el minimo de documentacion que exige el portal: "
            "descripcion funcional del API y de cada operacion, operationId, parametros descritos, "
            "respuestas 2xx/4xx documentadas, esquema de seguridad y ejemplos. "
            "No publica nada. Usar despues de cada iteracion de documentacion."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string", "description": "Ruta al archivo openapi.json o .yaml-convertido-a-json."},
                "threshold": {"type": "integer", "description": "Cobertura minima exigida (0-100). Por defecto 80."},
            },
            "required": ["spec_path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "devportal_publish_api",
        "description": (
            "Publica una spec OpenAPI en el Developer Portal. Antes de publicar aplica la misma "
            "puerta de calidad que devportal_validate_spec y rechaza la publicacion si hay bloqueantes "
            "(usar force=true solo con autorizacion explicita del desarrollador). "
            "Devuelve la ubicacion publicada, que es la fuente que despues consume la ingesta de Smart API Search."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string", "description": "Ruta al archivo openapi.json a publicar."},
                "name": {"type": "string", "description": "Nombre del API en el portal. Si se omite se deriva de info.title."},
                "version": {"type": "string", "description": "Version publicada. Si se omite se toma de info.version."},
                "owner": {"type": "string", "description": "Equipo responsable que se muestra en el portal."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Etiquetas de agrupacion en el catalogo."},
                "visibility": {
                    "type": "string",
                    "enum": ["public", "authenticated", "private"],
                    "description": "Visibilidad en el portal. Por defecto authenticated.",
                },
                "threshold": {"type": "integer", "description": "Cobertura minima exigida (0-100). Por defecto 80."},
                "dry_run": {"type": "boolean", "description": "Si es true valida y muestra que se publicaria, sin escribir en el portal."},
                "force": {"type": "boolean", "description": "Publica aunque existan bloqueantes de documentacion. Requiere autorizacion del desarrollador."},
            },
            "required": ["spec_path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "devportal_list_apis",
        "description": "Lista las APIs publicadas en el catalogo del Developer Portal, con su cobertura de documentacion y fecha de publicacion.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "devportal_get_api",
        "description": "Recupera del portal la spec ya publicada de un API. Sirve para verificar que lo publicado es lo esperado.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del API en el portal."},
                "version": {"type": "string", "description": "Version publicada."},
            },
            "required": ["name", "version"],
            "additionalProperties": False,
        },
    },
    {
        "name": "devportal_unpublish_api",
        "description": "Retira una publicacion del portal. Pensado para limpiar entre ejecuciones de la demo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre del API en el portal."},
                "version": {"type": "string", "description": "Version publicada."},
            },
            "required": ["name", "version"],
            "additionalProperties": False,
        },
    },
]


# --------------------------------------------------------------------- utilidades


def log(message: str) -> None:
    """Traza a stderr: stdout esta reservado para el protocolo."""
    print(f"[devportal] {message}", file=sys.stderr, flush=True)


def load_spec(spec_path: str) -> dict:
    path = Path(spec_path).expanduser()

    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    if not path.exists():
        raise PortalError(f"No existe la spec en {path}")

    try:
        # utf-8-sig: varias herramientas de Windows escriben el archivo con BOM.
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise PortalError(
            f"{path} no es JSON valido ({error}). "
            "Si la spec esta en YAML, conviertela a JSON antes de publicar."
        ) from error


def _spec_identity(spec: dict, name, version):
    info = spec.get("info") or {}
    resolved_name = name or info.get("title")
    resolved_version = version or info.get("version")

    if not resolved_name:
        raise PortalError("No se pudo determinar el nombre del API: pasa 'name' o define info.title en la spec.")
    if not resolved_version:
        raise PortalError("No se pudo determinar la version: pasa 'version' o define info.version en la spec.")

    return resolved_name, str(resolved_version)


# ----------------------------------------------------------------- herramientas


def tool_status(_args: dict) -> str:
    portal = Portal()
    lines = ["Developer Portal · destino de publicacion"]
    for key, value in portal.status().items():
        lines.append(f"  {key}: {value}")
    if portal.mode == "mock":
        lines.append("")
        lines.append("Modo mock: no se llama a ningun portal real; se escribe el catalogo local.")
    return "\n".join(lines)


def tool_validate_spec(args: dict) -> str:
    spec = load_spec(args["spec_path"])
    result = spec_check.check_spec(spec, int(args.get("threshold", spec_check.DEFAULT_THRESHOLD)))
    return spec_check.format_report(result)


def tool_publish_api(args: dict) -> str:
    portal = Portal()
    spec = load_spec(args["spec_path"])
    name, version = _spec_identity(spec, args.get("name"), args.get("version"))

    threshold = int(args.get("threshold", spec_check.DEFAULT_THRESHOLD))
    check = spec_check.check_spec(spec, threshold)
    report = spec_check.format_report(check)

    if not check["passed"] and not args.get("force"):
        raise PortalError(
            "PUBLICACION RECHAZADA: la documentacion no cumple el minimo del portal.\n\n"
            + report
            + "\n\nCorrige los bloqueantes en el codigo fuente, regenera la spec y vuelve a intentar."
        )

    header = f"API: {name} {version}\n{report}\n"

    if args.get("dry_run"):
        return (
            header
            + f"\nDRY RUN: no se publico nada. Destino: {portal.status()}"
        )

    meta = {
        "title": (spec.get("info") or {}).get("title", name),
        "owner": args.get("owner"),
        "tags": args.get("tags"),
        "visibility": args.get("visibility", "authenticated"),
        "operations": check["operations"],
        "doc_score": check["score"],
    }

    result = portal.publish(spec, name, version, meta)
    forced = "\nATENCION: publicado con force=true pese a los bloqueantes.\n" if not check["passed"] else ""

    return (
        header
        + forced
        + "\nPublicado en el Developer Portal:\n"
        + json.dumps(result, indent=2, ensure_ascii=False)
        + "\n\nLa ingesta de Smart API Search ya puede tomar esta fuente."
    )


def tool_list_apis(_args: dict) -> str:
    apis = Portal().list_apis()

    if not apis:
        return "El catalogo no tiene APIs publicadas."

    lines = [f"APIs publicadas ({len(apis)}):"]
    for api in apis:
        if isinstance(api, dict):
            score = api.get("doc_score")
            score_txt = f" · doc {score}%" if score is not None else ""
            lines.append(
                f"  - {api.get('name')} {api.get('version')} · {api.get('operations', '?')} operaciones"
                f"{score_txt} · {api.get('published_at', 'sin fecha')}"
            )
        else:
            lines.append(f"  - {api}")
    return "\n".join(lines)


def tool_get_api(args: dict) -> str:
    spec = Portal().get_api(args["name"], args["version"])
    return json.dumps(spec, indent=2, ensure_ascii=False)


def tool_unpublish_api(args: dict) -> str:
    result = Portal().unpublish(args["name"], args["version"])
    return json.dumps(result, indent=2, ensure_ascii=False)


HANDLERS = {
    "devportal_status": tool_status,
    "devportal_validate_spec": tool_validate_spec,
    "devportal_publish_api": tool_publish_api,
    "devportal_list_apis": tool_list_apis,
    "devportal_get_api": tool_get_api,
    "devportal_unpublish_api": tool_unpublish_api,
}


# --------------------------------------------------------------------- protocolo


def handle(message: dict):
    """Devuelve la respuesta JSON-RPC, o None si el mensaje es una notificacion."""
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params") or {}

    if msg_id is None:
        return None  # notificacion (p. ej. notifications/initialized)

    def ok(result):
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def fail(code, text):
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": text}}

    if method == "initialize":
        client = params.get("protocolVersion") or PROTOCOL_VERSION
        return ok({
            "protocolVersion": client if isinstance(client, str) else PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
        })

    if method == "ping":
        return ok({})

    if method == "tools/list":
        return ok({"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        handler = HANDLERS.get(name)

        if handler is None:
            return fail(-32602, f"Herramienta desconocida: {name}")

        try:
            text = handler(params.get("arguments") or {})
            return ok({"content": [{"type": "text", "text": text}], "isError": False})
        except PortalError as error:
            return ok({"content": [{"type": "text", "text": str(error)}], "isError": True})
        except KeyError as error:
            return ok({"content": [{"type": "text", "text": f"Falta el argumento {error}"}], "isError": True})
        except Exception as error:  # noqa: BLE001 - el cliente debe ver el detalle
            log(f"error en {name}: {error!r}")
            return ok({"content": [{"type": "text", "text": f"Error inesperado: {error}"}], "isError": True})

    return fail(-32601, f"Metodo no soportado: {method}")


def main() -> None:
    # En Windows la consola no usa UTF-8 por defecto: sin esto los acentos de las
    # descripciones romperian el JSON-RPC que lee el cliente MCP.
    for stream, errors in ((sys.stdin, "strict"), (sys.stdout, "strict"), (sys.stderr, "replace")):
        try:
            stream.reconfigure(encoding="utf-8", errors=errors)
        except (AttributeError, ValueError):
            pass

    try:
        log(f"listo · modo {Portal().mode}")
    except PortalError as error:
        log(f"configuracion invalida (se respondera con error en cada llamada): {error}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            log(f"mensaje ilegible: {line[:120]}")
            continue

        response = handle(message)

        if response is not None:
            # ensure_ascii=True: la linea que viaja por el protocolo queda en ASCII puro.
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
