from __future__ import annotations

from PySide6.QtWidgets import QApplication


def copy_to_clipboard(text: str) -> None:
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
