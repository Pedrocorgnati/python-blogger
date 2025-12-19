from __future__ import annotations

from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from core.package_builder import build_blog_admin_package, build_translator_package
from utils.io import load_json, save_json
from utils.logger import info, warn
from utils.paths import (
    ensure_app_dirs,
    get_data_dir,
    get_outputs_dir,
    get_repo_schema_path
)
from utils.validators import detect_accent_warning, validate_blog_url, validate_content_package, validate_slug


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("translator-app")
        self.resize(1200, 860)

        self.schema_path = get_repo_schema_path()
        ensure_app_dirs()

        self.import_button = QPushButton("Import Creator JSON")
        self.import_button.clicked.connect(self.handle_import)

        self.translation_key = QLineEdit()
        self.author = QLineEdit()
        self.blog_url = QLineEdit()
        self.link_policy = QComboBox()
        self.link_policy.addItems(["no-links", "blog-only", "blog-and-affiliate"])
        self.publish_all = QCheckBox("Publish all locales")
        self.publish_all.setChecked(True)
        self.default_affiliate_disclosure = QCheckBox("Default affiliate disclosure")

        self.save_draft_button = QPushButton("Save Draft")
        self.save_draft_button.clicked.connect(self.handle_save_draft)
        self.load_draft_button = QPushButton("Load Draft")
        self.load_draft_button.clicked.connect(self.handle_load_draft)
        self.export_button = QPushButton("Export Translator Package JSON")
        self.export_button.clicked.connect(self.handle_export)
        self.export_admin_button = QPushButton("Export Blog Admin Package JSON")
        self.export_admin_button.clicked.connect(self.handle_export_admin)

        self.locale_fields = {}
        self._created_at = ""
        self._setup_locale_fields()

        layout = QVBoxLayout()
        layout.addWidget(self._build_top())
        layout.addWidget(self._build_locales())
        self.setLayout(layout)

    def _build_top(self) -> QWidget:
        group = QGroupBox("Global")
        form = QFormLayout()
        form.addRow("", self.import_button)
        form.addRow("translationKey", self.translation_key)
        form.addRow("author", self.author)
        form.addRow("blogUrl", self.blog_url)
        form.addRow("linkPolicy", self.link_policy)
        form.addRow("", self.publish_all)
        form.addRow("", self.default_affiliate_disclosure)

        buttons = QHBoxLayout()
        buttons.addWidget(self.load_draft_button)
        buttons.addWidget(self.save_draft_button)
        buttons.addWidget(self.export_button)
        buttons.addWidget(self.export_admin_button)
        buttons.addStretch(1)
        form.addRow(buttons)
        group.setLayout(form)
        return group

    def _setup_locale_fields(self) -> None:
        for locale in ["en", "pt", "es", "it"]:
            self.locale_fields[locale] = {
                "title": QLineEdit(),
                "description": QLineEdit(),
                "slug": QLineEdit(),
                "content": QTextEdit(),
                "tags": QLineEdit(),
                "category": QLineEdit(),
                "keywords": QLineEdit(),
                "affiliate_enabled": QCheckBox("Affiliate enabled"),
                "affiliate_url": QLineEdit(),
                "affiliate_disclosure": QLineEdit()
            }
            self.locale_fields[locale]["content"].setMinimumHeight(200)

    def _build_locales(self) -> QWidget:
        group = QGroupBox("Locales")
        grid = QGridLayout()
        locales = ["en", "pt", "es", "it"]
        for idx, locale in enumerate(locales):
            box = QGroupBox(locale.upper())
            form = QFormLayout()
            form.addRow("Title", self.locale_fields[locale]["title"])
            form.addRow("Description", self.locale_fields[locale]["description"])
            form.addRow("Slug", self.locale_fields[locale]["slug"])
            form.addRow("Content", self.locale_fields[locale]["content"])
            form.addRow("Tags", self.locale_fields[locale]["tags"])
            form.addRow("Category", self.locale_fields[locale]["category"])
            form.addRow("Keywords", self.locale_fields[locale]["keywords"])
            form.addRow("", self.locale_fields[locale]["affiliate_enabled"])
            form.addRow("Affiliate URL", self.locale_fields[locale]["affiliate_url"])
            form.addRow("Affiliate disclosure", self.locale_fields[locale]["affiliate_disclosure"])
            box.setLayout(form)
            row = idx // 2
            col = idx % 2
            grid.addWidget(box, row, col)
        group.setLayout(grid)
        return group

    def _collect_locales(self) -> dict:
        locales = {}
        for locale, fields in self.locale_fields.items():
            locales[locale] = {
                "title": fields["title"].text().strip(),
                "description": fields["description"].text().strip(),
                "slug": fields["slug"].text().strip(),
                "content": fields["content"].toPlainText().strip(),
                "tags": [tag.strip() for tag in fields["tags"].text().split(",") if tag.strip()],
                "category": fields["category"].text().strip(),
                "keywords": [kw.strip() for kw in fields["keywords"].text().split(",") if kw.strip()],
                "affiliate": {
                    "enabled": fields["affiliate_enabled"].isChecked(),
                    "url": fields["affiliate_url"].text().strip(),
                    "disclosure": fields["affiliate_disclosure"].text().strip()
                }
            }
        return locales

    def handle_import(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Creator JSON", "", "JSON Files (*.json)")
        if not file_name:
            return
        data = load_json(file_name)
        if not data:
            return
        errors = validate_content_package(data, self.schema_path)
        if errors:
            QMessageBox.critical(self, "Invalid package", "\n".join(errors))
            return
        meta = data.get("meta", {})
        self._created_at = meta.get("createdAt", "")
        global_data = data.get("global", {})
        self.translation_key.setText(meta.get("translationKey", ""))
        self.author.setText(global_data.get("author", ""))
        self.blog_url.setText(global_data.get("blogUrl", ""))
        self.link_policy.setCurrentText(global_data.get("linkPolicy", "no-links"))
        self.default_affiliate_disclosure.setChecked(global_data.get("defaultAffiliateDisclosure", False))

        locales = data.get("locales", {})
        for locale in ["en", "pt", "es", "it"]:
            loc = locales.get(locale, {})
            self.locale_fields[locale]["title"].setText(loc.get("title", ""))
            self.locale_fields[locale]["description"].setText(loc.get("description", ""))
            self.locale_fields[locale]["slug"].setText(loc.get("slug", ""))
            self.locale_fields[locale]["content"].setPlainText(loc.get("content", ""))
            self.locale_fields[locale]["tags"].setText(", ".join(loc.get("tags", []) or []))
            self.locale_fields[locale]["category"].setText(loc.get("category", ""))
            self.locale_fields[locale]["keywords"].setText(", ".join(loc.get("keywords", []) or []))
            affiliate = loc.get("affiliate", {})
            self.locale_fields[locale]["affiliate_enabled"].setChecked(affiliate.get("enabled", False))
            self.locale_fields[locale]["affiliate_url"].setText(affiliate.get("url", ""))
            self.locale_fields[locale]["affiliate_disclosure"].setText(affiliate.get("disclosure", ""))

        self._apply_read_only_en()
        info("Creator JSON imported")

    def _apply_read_only_en(self) -> None:
        for key, field in self.locale_fields["en"].items():
            if hasattr(field, "setReadOnly"):
                field.setReadOnly(True)
            if isinstance(field, QCheckBox):
                field.setEnabled(False)

    def handle_export(self) -> None:
        if not self.translation_key.text().strip():
            QMessageBox.warning(self, "Missing", "translationKey is required")
            return
        if not self.author.text().strip():
            QMessageBox.warning(self, "Missing", "author is required")
            return
        if not validate_blog_url(self.blog_url.text().strip()):
            QMessageBox.warning(self, "Invalid", "blogUrl is invalid")
            return

        locales = self._collect_locales()
        if not locales["en"]["content"]:
            QMessageBox.warning(self, "Missing", "EN content is required")
            return

        for locale in ["en", "pt", "es", "it"]:
            if locales[locale]["slug"] and not validate_slug(locales[locale]["slug"]):
                QMessageBox.warning(self, "Invalid", f"Invalid slug in {locale.upper()}")
                return

        if self.publish_all.isChecked():
            missing = [
                locale for locale in ["pt", "es", "it"]
                if not locales[locale]["content"] or not locales[locale]["title"] or not locales[locale]["description"]
            ]
            if missing:
                QMessageBox.critical(self, "Missing", "Missing locales: " + ", ".join(missing))
                return

        if detect_accent_warning(locales["en"]["content"]):
            QMessageBox.warning(self, "Warning", "EN content contains accented chars; verify locale.")

        base = {
            "meta": {
                "translationKey": self.translation_key.text().strip(),
                "createdAt": self._created_at or datetime.utcnow().isoformat(),
                "updatedAt": "",
                "source": "translator",
                "publishAllLocales": self.publish_all.isChecked(),
                "localesIncluded": []
            },
            "global": {
                "author": self.author.text().strip(),
                "blogUrl": self.blog_url.text().strip(),
                "linkPolicy": self.link_policy.currentText(),
                "defaultAffiliateDisclosure": self.default_affiliate_disclosure.isChecked()
            }
        }

        locales_included = [locale for locale in ["en", "pt", "es", "it"] if locales[locale]["content"]]
        payload = build_translator_package(
            base,
            locales,
            self.publish_all.isChecked(),
            locales_included
        )
        errors = validate_content_package(payload, self.schema_path)
        if errors:
            QMessageBox.critical(self, "Schema error", "\n".join(errors))
            return

        export_dir = get_outputs_dir() / "content-packages"
        path = export_dir / f"{self.translation_key.text().strip()}-translator.json"
        if save_json(path, payload):
            QMessageBox.information(self, "Exported", f"Saved to {path}")

    def handle_export_admin(self) -> None:
        locales = self._collect_locales()
        payload = build_blog_admin_package(self.translation_key.text().strip(), locales)
        export_dir = get_outputs_dir() / "blog-admin"
        path = export_dir / f"{self.translation_key.text().strip()}-blog-admin.json"
        if save_json(path, payload):
            QMessageBox.information(self, "Exported", f"Saved to {path}")

    def handle_save_draft(self) -> None:
        if not self.translation_key.text().strip():
            QMessageBox.warning(self, "Missing", "translationKey is required")
            return
        payload = {
            "meta": {
                "translationKey": self.translation_key.text().strip()
            },
            "global": {
                "author": self.author.text().strip(),
                "blogUrl": self.blog_url.text().strip(),
                "linkPolicy": self.link_policy.currentText(),
                "defaultAffiliateDisclosure": self.default_affiliate_disclosure.isChecked()
            },
            "locales": self._collect_locales()
        }
        draft_path = get_data_dir() / "drafts" / f"{self.translation_key.text().strip()}-translator.json"
        save_json(draft_path, payload)

    def handle_load_draft(self) -> None:
        draft_dir = get_data_dir() / "drafts"
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Draft", str(draft_dir), "JSON Files (*.json)"
        )
        if not file_name:
            return
        data = load_json(file_name)
        if not data:
            return
        self.translation_key.setText(data.get("meta", {}).get("translationKey", ""))
        global_data = data.get("global", {})
        self.author.setText(global_data.get("author", ""))
        self.blog_url.setText(global_data.get("blogUrl", ""))
        self.link_policy.setCurrentText(global_data.get("linkPolicy", "no-links"))
        self.default_affiliate_disclosure.setChecked(global_data.get("defaultAffiliateDisclosure", False))
        locales = data.get("locales", {})
        for locale in ["en", "pt", "es", "it"]:
            loc = locales.get(locale, {})
            self.locale_fields[locale]["title"].setText(loc.get("title", ""))
            self.locale_fields[locale]["description"].setText(loc.get("description", ""))
            self.locale_fields[locale]["slug"].setText(loc.get("slug", ""))
            self.locale_fields[locale]["content"].setPlainText(loc.get("content", ""))
            self.locale_fields[locale]["tags"].setText(", ".join(loc.get("tags", []) or []))
            self.locale_fields[locale]["category"].setText(loc.get("category", ""))
            self.locale_fields[locale]["keywords"].setText(", ".join(loc.get("keywords", []) or []))
            affiliate = loc.get("affiliate", {})
            self.locale_fields[locale]["affiliate_enabled"].setChecked(affiliate.get("enabled", False))
            self.locale_fields[locale]["affiliate_url"].setText(affiliate.get("url", ""))
            self.locale_fields[locale]["affiliate_disclosure"].setText(affiliate.get("disclosure", ""))
        self._apply_read_only_en()
        warn(f"Draft loaded from {file_name}")
