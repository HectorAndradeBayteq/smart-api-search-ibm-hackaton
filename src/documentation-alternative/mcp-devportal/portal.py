"""Adaptadores de publicacion hacia el Developer Portal.

Tres modos, elegidos con la variable de entorno DEVPORTAL_MODE:

  mock     (por defecto) escribe en un directorio local que simula el portal.
           Es lo que se usa en la demo: no depende de red ni credenciales, y
           deja un catalogo que el proceso de ingesta de SmAS puede leer.
  apic     IBM API Connect: sube la spec como draft API y, opcionalmente,
           publica el producto en un catalogo.
  generic  cualquier portal con un endpoint REST que reciba la spec en JSON.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_STORE = Path(__file__).resolve().parent.parent / "portal-store"


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "api"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PortalError(RuntimeError):
    """Error de publicacion que el agente debe mostrar tal cual."""


class Portal:
    """Fachada unica; el agente no sabe contra que backend esta hablando."""

    def __init__(self) -> None:
        self.mode = _env("DEVPORTAL_MODE", "mock").lower()
        self.base_url = _env("DEVPORTAL_BASE_URL").rstrip("/")
        self.token = _env("DEVPORTAL_TOKEN")
        self.org = _env("DEVPORTAL_ORG")
        self.catalog = _env("DEVPORTAL_CATALOG", "sandbox")
        self.timeout = int(_env("DEVPORTAL_TIMEOUT", "30"))
        self.insecure = _env("DEVPORTAL_INSECURE", "false").lower() == "true"
        self.store = Path(_env("DEVPORTAL_STORE") or DEFAULT_STORE)

        if self.mode not in ("mock", "apic", "generic"):
            raise PortalError(f"DEVPORTAL_MODE invalido: {self.mode} (usar mock, apic o generic)")

        if self.mode != "mock" and not self.base_url:
            raise PortalError(f"DEVPORTAL_MODE={self.mode} requiere DEVPORTAL_BASE_URL")

    # ---------------------------------------------------------------- estado

    def status(self) -> dict:
        info = {
            "mode": self.mode,
            "catalog": self.catalog,
        }
        if self.mode == "mock":
            info["store"] = str(self.store)
            info["published_apis"] = len(self._index().get("apis", []))
        else:
            info["base_url"] = self.base_url
            info["org"] = self.org or "(sin definir)"
            info["token"] = "definido" if self.token else "AUSENTE"
        return info

    # ------------------------------------------------------------- publicar

    def publish(self, spec: dict, name: str, version: str, meta: dict) -> dict:
        if self.mode == "mock":
            return self._publish_mock(spec, name, version, meta)
        if self.mode == "apic":
            return self._publish_apic(spec, name, version, meta)
        return self._publish_generic(spec, name, version, meta)

    def list_apis(self) -> list:
        if self.mode == "mock":
            return self._index().get("apis", [])
        payload = self._http("GET", self._list_url(), None)
        if isinstance(payload, dict):
            return payload.get("results") or payload.get("apis") or []
        return payload if isinstance(payload, list) else []

    def get_api(self, name: str, version: str) -> dict:
        if self.mode == "mock":
            path = self._spec_path(name, version)
            if not path.exists():
                raise PortalError(f"No hay publicacion para {name} {version} en {self.store}")
            return json.loads(path.read_text(encoding="utf-8"))
        return self._http("GET", f"{self._list_url()}/{slugify(name)}-{version}", None)

    def unpublish(self, name: str, version: str) -> dict:
        if self.mode == "mock":
            path = self._spec_path(name, version)
            existed = path.exists()
            if existed:
                path.unlink()
            index = self._index()
            index["apis"] = [
                a for a in index.get("apis", [])
                if not (a["name"] == name and a["version"] == version)
            ]
            index["updated_at"] = _now()
            self._write_index(index)
            return {"removed": existed, "name": name, "version": version}
        return self._http("DELETE", f"{self._list_url()}/{slugify(name)}-{version}", None)

    # ------------------------------------------------------------ backend: mock

    def _spec_path(self, name: str, version: str) -> Path:
        return self.store / "apis" / f"{slugify(name)}-{version}.json"

    def _index_path(self) -> Path:
        return self.store / "catalog.json"

    def _index(self) -> dict:
        path = self._index_path()
        if not path.exists():
            return {"catalog": self.catalog, "updated_at": None, "apis": []}
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_index(self, index: dict) -> None:
        self.store.mkdir(parents=True, exist_ok=True)
        self._index_path().write_text(
            json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _publish_mock(self, spec: dict, name: str, version: str, meta: dict) -> dict:
        target = self._spec_path(name, version)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        entry = {
            "name": name,
            "version": version,
            "title": (spec.get("info") or {}).get("title", name),
            "catalog": self.catalog,
            "visibility": meta.get("visibility", "authenticated"),
            "owner": meta.get("owner"),
            "tags": meta.get("tags") or [],
            "operations": meta.get("operations"),
            "doc_score": meta.get("doc_score"),
            "spec_file": str(target.relative_to(self.store)).replace("\\", "/"),
            "published_at": _now(),
        }

        index = self._index()
        index["catalog"] = self.catalog
        index["apis"] = [
            a for a in index.get("apis", [])
            if not (a["name"] == name and a["version"] == version)
        ] + [entry]
        index["apis"].sort(key=lambda a: (a["name"], a["version"]))
        index["updated_at"] = _now()
        self._write_index(index)

        return {
            "backend": "mock",
            "location": str(target),
            "catalog_index": str(self._index_path()),
            "entry": entry,
        }

    # ------------------------------------------------------------ backend: apic

    def _publish_apic(self, spec: dict, name: str, version: str, meta: dict) -> dict:
        if not self.org:
            raise PortalError("DEVPORTAL_MODE=apic requiere DEVPORTAL_ORG (provider organization)")

        draft_url = f"{self.base_url}/api/orgs/{self.org}/drafts/draft-apis"
        created = self._http("POST", draft_url, {"openapi": spec})

        result = {
            "backend": "apic",
            "draft_url": draft_url,
            "draft": created,
        }

        if _env("DEVPORTAL_PUBLISH", "false").lower() == "true":
            product = {
                "product": "1.0.0",
                "info": {
                    "name": slugify(name),
                    "title": meta.get("title", name),
                    "version": version,
                },
                "apis": {"main": {"name": f"{slugify(name)}:{version}"}},
                "visibility": {
                    "view": {"type": meta.get("visibility", "authenticated")},
                    "subscribe": {"type": "authenticated"},
                },
            }
            publish_url = f"{self.base_url}/api/catalogs/{self.org}/{self.catalog}/publish"
            result["publish_url"] = publish_url
            result["publish"] = self._http("POST", publish_url, {"product": product})

        return result

    # --------------------------------------------------------- backend: generic

    def _list_url(self) -> str:
        return self.base_url + _env("DEVPORTAL_APIS_PATH", "/apis")

    def _publish_generic(self, spec: dict, name: str, version: str, meta: dict) -> dict:
        url = self._list_url()
        payload = {
            "name": slugify(name),
            "version": version,
            "catalog": self.catalog,
            "visibility": meta.get("visibility", "authenticated"),
            "owner": meta.get("owner"),
            "tags": meta.get("tags") or [],
            "openapi": spec,
        }
        return {"backend": "generic", "url": url, "response": self._http("POST", url, payload)}

    # ------------------------------------------------------------------- http

    def _http(self, method: str, url: str, body):
        data = None
        headers = {"Accept": "application/json"}

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        context = ssl._create_unverified_context() if self.insecure else None

        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=context) as response:
                raw = response.read().decode("utf-8").strip()
                if not raw:
                    return {"status": response.status}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"status": response.status, "body": raw[:2000]}
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:2000]
            raise PortalError(f"{method} {url} -> HTTP {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise PortalError(f"{method} {url} -> sin conexion: {error.reason}") from error
