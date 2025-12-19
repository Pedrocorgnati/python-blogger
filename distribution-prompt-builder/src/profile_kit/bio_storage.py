from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .bio_models import BioKit
from PySide6.QtWidgets import QMessageBox
from utils.logger import error as log_error
from utils.logger import info as log_info


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_bios_json(path: str | Path, kit: BioKit) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    try:
        with target.open("w", encoding="utf-8") as handle:
            json.dump(kit.to_dict(), handle, indent=2)
        log_info(f"Saved bios JSON to {target}")
    except Exception as exc:
        log_error(f"Failed to save bios JSON to {target}: {exc}")
        QMessageBox.critical(None, "Save error", f"Failed to save bios JSON: {exc}")


def save_bios_md(path: str | Path, kit: BioKit) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    lines = []
    for locale, channels in kit.to_dict().items():
        lines.append(f"# {locale.upper()}\n")
        for channel, fields in channels.items():
            lines.append(f"## {channel}\n")
            for key, value in fields.items():
                lines.append(f"**{key}**\n")
                lines.append(f"{value or ''}\n")
            lines.append("\n")
        lines.append("\n")

    try:
        with target.open("w", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
        log_info(f"Saved bios MD to {target}")
    except Exception as exc:
        log_error(f"Failed to save bios MD to {target}: {exc}")
        QMessageBox.critical(None, "Save error", f"Failed to save bios MD: {exc}")


def save_runtime_copy(path: str | Path, kit: BioKit) -> None:
    target = Path(path)
    ensure_dir(target.parent)
    try:
        with target.open("w", encoding="utf-8") as handle:
            json.dump(kit.to_dict(), handle, indent=2)
        log_info(f"Saved runtime bios to {target}")
    except Exception as exc:
        log_error(f"Failed to save runtime bios to {target}: {exc}")
        QMessageBox.critical(None, "Save error", f"Failed to save runtime bios: {exc}")
