from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from PySide6.QtWidgets import QMessageBox

from core.models import PromptResult
from utils.logger import error as log_error
from utils.logger import info as log_info
from utils.validators import validate_content_package


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_all_prompts(base_dir: str, translation_key: str, prompts: List[PromptResult]) -> str:
    ensure_dir(base_dir)
    file_path = os.path.join(base_dir, f"{translation_key}-distribution-prompts.txt")
    content = "\n\n".join([item.prompt_text for item in prompts])
    try:
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        log_info(f"Saved prompts to {file_path}")
        return file_path
    except Exception as exc:
        log_error(f"Failed to save prompts: {exc}")
        QMessageBox.critical(None, "Save error", f"Failed to save prompts: {exc}")
        return ""


def save_per_channel(base_dir: str, translation_key: str, bundle_by_channel: Dict[str, str]) -> List[str]:
    channel_dir = os.path.join(base_dir, translation_key)
    ensure_dir(channel_dir)
    paths: List[str] = []
    for channel, text in bundle_by_channel.items():
        file_path = os.path.join(channel_dir, f"{channel.lower().replace('.', '')}-bundle.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(text)
            paths.append(file_path)
        except Exception as exc:
            log_error(f"Failed to save channel prompt {channel}: {exc}")
            QMessageBox.critical(None, "Save error", f"Failed to save {channel}: {exc}")
    return paths


def save_results_templates(base_dir: str, translation_key: str, channels: List[str]) -> List[str]:
    results_dir = os.path.join(base_dir, translation_key)
    ensure_dir(results_dir)
    paths: List[str] = []
    for channel in channels:
        file_path = os.path.join(results_dir, f"{channel.lower().replace('.', '')}-results.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write("")
            paths.append(file_path)
        except Exception as exc:
            log_error(f"Failed to save results template {channel}: {exc}")
            QMessageBox.critical(None, "Save error", f"Failed to save results template: {exc}")
    return paths


def load_content_package(file_path: str, schema_path: str) -> Tuple[Dict[str, object], List[str]]:
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = handle.read()
    except Exception as exc:
        log_error(f"Failed to read content package: {exc}")
        QMessageBox.critical(None, "Read error", f"Failed to read content package: {exc}")
        return {}, ["Failed to read content package."]

    try:
        payload = json.loads(data)
    except Exception as exc:
        log_error(f"Invalid JSON: {exc}")
        return {}, ["Invalid JSON."]

    errors = validate_content_package(payload, schema_path)
    if errors:
        log_error("Content package validation errors: " + "; ".join(errors))
    return payload if not errors else {}, errors
