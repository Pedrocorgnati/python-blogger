from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import QMessageBox

from utils.logger import error as log_error
from utils.logger import info as log_info


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_json(path: str | Path, payload: Dict[str, object]) -> bool:
    target = Path(path)
    ensure_dir(target.parent)
    try:
        with target.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        log_info(f"Saved JSON to {target}")
        return True
    except Exception as exc:
        log_error(f"Failed to save JSON to {target}: {exc}")
        QMessageBox.critical(None, "Save error", f"Failed to save JSON to {target}: {exc}")
        return False


def load_json(path: str | Path) -> Dict[str, object] | None:
    target = Path(path)
    try:
        with target.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        log_error(f"Failed to load JSON from {target}: {exc}")
        QMessageBox.critical(None, "Load error", f"Failed to load JSON from {target}: {exc}")
        return None
