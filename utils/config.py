"""Configuracion del framework mediante biblioteca estandar y entorno."""

import math
import os
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SELENIUM_CACHE_DIR = PROJECT_ROOT / ".tools" / "selenium"
DEFAULT_BASE_URL = "https://www.saucedemo.com/"
DEFAULT_SELENIUM_TIMEOUT = 10


def get_base_url():
    value = os.getenv("BASE_URL", DEFAULT_BASE_URL).strip()
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("BASE_URL debe ser una URL http o https valida")
    return value


def get_selenium_timeout():
    try:
        value = float(os.getenv("SELENIUM_TIMEOUT", str(DEFAULT_SELENIUM_TIMEOUT)))
    except ValueError as error:
        raise ValueError("SELENIUM_TIMEOUT debe ser un numero positivo") from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError("SELENIUM_TIMEOUT debe ser un numero positivo y finito")
    return value


def resolve_path(value):
    """Las rutas relativas se interpretan desde la raiz del proyecto."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def get_evidence_root(value=None):
    selected = value if value is not None else os.getenv("EVIDENCE_DIR", "reports/runs")
    if not selected.strip():
        raise ValueError("El directorio de evidencias no puede estar vacio")
    return resolve_path(selected)
