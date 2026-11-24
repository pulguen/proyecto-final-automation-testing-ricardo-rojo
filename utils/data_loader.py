"""Lectura y validación de casos externos sin dependencias adicionales."""

import csv
import json

from utils.config import resolve_path


def _validate_cases(cases, path, required_fields, allow_empty_fields):
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{path}: se esperaba una lista no vacía de casos")
    seen_ids = set()
    for number, case in enumerate(cases, start=1):
        location = f"{path}, registro {number}"
        if not isinstance(case, dict):
            raise ValueError(f"{location}: cada caso debe ser un objeto con campos")
        for field in ("id", *required_fields):
            if field not in case:
                raise ValueError(f"{location}: falta el campo obligatorio {field!r}")
            value = case[field]
            if value is None:
                raise ValueError(f"{location}: el campo {field!r} no puede ser null")
            if isinstance(value, str) and not value.strip() and field not in allow_empty_fields:
                raise ValueError(f"{location}: el campo {field!r} no puede estar vacío")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{location}: id debe ser un texto no vacío")
        if case_id in seen_ids:
            raise ValueError(f"{location}: id duplicado {case_id!r}")
        seen_ids.add(case_id)
    return cases


def load_json_cases(file_path, required_fields, allow_empty_fields=()):
    """Leer una lista de casos JSON; las rutas relativas parten del proyecto."""
    path = resolve_path(file_path)
    try:
        with path.open(encoding="utf-8-sig") as file:
            cases = json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"No existe el archivo de datos JSON: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON inválido en {path}: línea {error.lineno}, columna {error.colno}"
        ) from error
    except (OSError, UnicodeError) as error:
        raise ValueError(f"No se pudo leer el archivo JSON {path}: {error}") from error
    return _validate_cases(cases, path, required_fields, allow_empty_fields)


def load_csv_cases(file_path, required_fields, allow_empty_fields=()):
    """Leer CSV con encabezados; los valores de las celdas se conservan como texto."""
    path = resolve_path(file_path)
    try:
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            headers = reader.fieldnames
            if not headers or any(not name.strip() for name in headers):
                raise ValueError(f"{path}: el CSV debe tener encabezados no vacíos")
            if len(headers) != len(set(headers)):
                raise ValueError(f"{path}: el CSV contiene encabezados duplicados")
            for field in ("id", *required_fields):
                if field not in headers:
                    raise ValueError(f"{path}: falta la columna obligatoria {field!r}")
            cases = list(reader)
            for number, case in enumerate(cases, start=1):
                if None in case:
                    raise ValueError(f"{path}, registro {number}: hay columnas sin encabezado")
    except FileNotFoundError as error:
        raise FileNotFoundError(f"No existe el archivo de datos CSV: {path}") from error
    except csv.Error as error:
        raise ValueError(f"CSV inválido en {path}: {error}") from error
    except (OSError, UnicodeError) as error:
        raise ValueError(f"No se pudo leer el archivo CSV {path}: {error}") from error
    return _validate_cases(cases, path, required_fields, allow_empty_fields)
