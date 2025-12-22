from __future__ import annotations

from pathlib import Path
import sys
import time


def get_app_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_repo_root() -> Path | None:
    start = get_app_root()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
        if (candidate / "package.json").is_file() and (candidate / "app").is_dir():
            return candidate
    return None


def _log_warning(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_file = get_logs_dir() / "errors.log"
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] WARN: {message}\n")
    except Exception:
        pass
    print(f"WARNING: {message}", file=sys.stderr)


def get_repo_schema_path() -> Path:
    # Prefer the nearest schemas/content_package.schema.json up the tree.
    start = get_app_root()
    for candidate in [start, *start.parents]:
        schema_path = candidate / "schemas" / "content_package.schema.json"
        if schema_path.exists():
            return schema_path

    fallback = get_app_root() / "schemas" / "content_package.schema.json"
    if fallback.exists():
        _log_warning(f"Repo schema not found. Using app-local schema at {fallback}")
        return fallback

    _log_warning(f"Schema not found. Expected {fallback}")
    return fallback


def get_outputs_dir() -> Path:
    return get_app_root() / "outputs"


def get_data_dir() -> Path:
    return get_app_root() / "data"


def get_logs_dir() -> Path:
    return get_app_root() / "logs"


def ensure_app_dirs() -> None:
    for directory in [get_outputs_dir(), get_data_dir(), get_logs_dir()]:
        directory.mkdir(parents=True, exist_ok=True)
