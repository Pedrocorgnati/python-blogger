from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from jsonschema import Draft7Validator
from utils.logger import error as log_error


def validate_blog_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_slug(value: str) -> bool:
    if not value:
        return False
    return re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value) is not None


def validate_content_package(payload: Dict[str, object], schema_path: str | Path) -> List[str]:
    path = Path(schema_path)
    if not path.exists():
        log_error(f"Schema file not found at {path}")
        return ["Schema file not found."]
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log_error(f"Failed to read schema at {path}: {exc}")
        return [f"Failed to read schema: {exc}"]

    validator = Draft7Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
        path = ".".join([str(item) for item in err.path]) or "root"
        errors.append(f"{path}: {err.message}")
    return errors


def detect_accent_warning(text: str) -> bool:
    accents = "áéíóúãõçñàèìòùâêîôû"
    return any(char in text.lower() for char in accents)
