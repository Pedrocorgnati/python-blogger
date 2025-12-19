from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


APPS = {
    "creator-app": Path("creator-app"),
    "translator-app": Path("translator-app"),
    "distribution-prompt-builder": Path("distribution-prompt-builder")
}


def load_paths_module(app_root: Path, name: str):
    module_path = app_root / "src" / "utils" / "paths.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Missing paths.py at {module_path}")
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load module for {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_app(app_root: Path, label: str) -> Path:
    paths = load_paths_module(app_root, f"paths_{label}")
    repo_root = paths.find_repo_root()
    if repo_root is None:
        raise RuntimeError(f"[{label}] repo root not found from {app_root}")
    schema_path = Path(paths.get_repo_schema_path())
    if not schema_path.exists():
        raise RuntimeError(f"[{label}] schema missing at {schema_path}")

    paths.ensure_app_dirs()
    for directory in [paths.get_outputs_dir(), paths.get_data_dir(), paths.get_logs_dir()]:
        if not Path(directory).exists():
            raise RuntimeError(f"[{label}] expected directory missing: {directory}")

    print(f"[{label}] repo_root={repo_root}")
    print(f"[{label}] schema={schema_path}")
    return schema_path


def validate_schema(schema_path: Path) -> None:
    try:
        import jsonschema
    except Exception:
        print("jsonschema not installed; skipping schema validation.")
        return

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)
    print(f"Schema OK: {schema_path}")


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    schema_paths = []
    for label, relative in APPS.items():
        app_root = base / relative
        schema_paths.append(check_app(app_root, label))

    if schema_paths:
        validate_schema(schema_paths[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
