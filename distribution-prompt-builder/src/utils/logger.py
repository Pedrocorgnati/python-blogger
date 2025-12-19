from __future__ import annotations

import os
import time

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "errors.log")


def _write(level: str, message: str) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {level.upper()}: {message}\n")


def info(message: str) -> None:
    _write("info", message)


def warn(message: str) -> None:
    _write("warn", message)


def error(message: str) -> None:
    _write("error", message)
