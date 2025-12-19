from __future__ import annotations

import time

from utils.paths import get_logs_dir

LOG_FILE = get_logs_dir() / "errors.log"


def _write(level: str, message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {level.upper()}: {message}\n")


def info(message: str) -> None:
    _write("info", message)


def warn(message: str) -> None:
    _write("warn", message)


def error(message: str) -> None:
    _write("error", message)
