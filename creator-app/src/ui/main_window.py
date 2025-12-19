from __future__ import annotations

from pathlib import Path
import json
import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from core.models import CreatorInputs
from core.package_builder import build_content_package
from utils.io import load_json, save_json
from utils.logger import info
from utils.paths import (
    ensure_app_dirs,
    get_data_dir,
    get_outputs_dir,
    get_repo_schema_path
)
from utils.validators import validate_blog_url, validate_content_package, validate_slug
from utils.blog_index import load_latest_blog_themes


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("creator-app")
        self.resize(1000, 800)

        self.schema_path = get_repo_schema_path()
        ensure_app_dirs()

        self._latest_themes: list[dict] = []
        self._theme_state = {
            "niche_context": "tech career skills that pay",
            "target_audience": "international audience in English; developers and career changers",
            "monetization_constraints": "only info-products affiliate; no physical products",
            "constraints": "evergreen + high search intent + relatable + not too broad",
            "avoid_topics": "",
            "prompt": "",
            "pasted_results": "",
            "suggested_themes": []
        }
        self._theme_draft_path: Path | None = None
        self._theme_autosave_timer = QTimer(self)
        self._theme_autosave_timer.setSingleShot(True)
        self._theme_autosave_timer.timeout.connect(self._autosave_theme_draft)
        self._theme_dialog: ThemeGeneratorDialog | None = None

        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("e.g., 'Top Tech Skills That Pay in 2026'")
        self.theme_input.textChanged.connect(self._schedule_theme_autosave)

        self.theme_next_button = QPushButton("Next")
        self.theme_next_button.clicked.connect(self._handle_theme_next)
        self.theme_create_button = QPushButton("Create Theme")
        self.theme_create_button.clicked.connect(self._open_create_theme_dialog)
        self.theme_import_button = QPushButton("Import latest blog themes")
        self.theme_import_button.clicked.connect(self._handle_import_latest_themes)
        self.theme_save_draft_button = QPushButton("Save Draft")
        self.theme_save_draft_button.clicked.connect(self._save_theme_draft)
        self.theme_load_draft_button = QPushButton("Load Draft")
        self.theme_load_draft_button.clicked.connect(self._load_theme_draft)

        self.latest_themes_list = QListWidget()
        self.latest_themes_list.itemClicked.connect(self._handle_latest_theme_clicked)
        self.copy_latest_themes_button = QPushButton("Copy list")
        self.copy_latest_themes_button.clicked.connect(self._copy_latest_themes)

        self.theme = QLineEdit()
        self.translation_key = QLineEdit()
        self.author = QLineEdit()
        self.blog_url = QLineEdit()
        self.title = QLineEdit()
        self.description = QLineEdit()
        self.slug = QLineEdit()
        self.slug.textChanged.connect(self._maybe_set_translation_key)
        self.tags = QLineEdit()
        self.category = QLineEdit()
        self.keywords = QLineEdit()
        self.content = QTextEdit()
        self.content.setMinimumHeight(280)

        self.link_policy = QComboBox()
        self.link_policy.addItems(["no-links", "blog-only", "blog-and-affiliate"])
        self.default_affiliate_disclosure = QCheckBox("Default affiliate disclosure")

        self.affiliate_enabled = QCheckBox("Affiliate enabled")
        self.affiliate_url = QLineEdit()
        self.affiliate_disclosure = QLineEdit()

        self.save_draft_button = QPushButton("Save Draft")
        self.save_draft_button.clicked.connect(self.handle_save_draft)
        self.load_draft_button = QPushButton("Load Draft")
        self.load_draft_button.clicked.connect(self.handle_load_draft)
        self.export_button = QPushButton("Export Content Package JSON")
        self.export_button.clicked.connect(self.handle_export)

        layout = QVBoxLayout()
        layout.addLayout(self._build_stepper())
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_theme_page())
        self.stack.addWidget(self._build_form())
        self.stack.addWidget(self._build_placeholder_page("Translator (PT/ES/IT)", 2))
        self.stack.addWidget(self._build_placeholder_page("Preview/Edit + Publish", 3))
        self.stack.addWidget(self._build_placeholder_page("Distribution", 4))
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self._set_step(0)

    def _build_form(self) -> QWidget:
        group = QGroupBox("Creator (EN)")
        form = QFormLayout()
        form.addRow("Theme", self.theme)
        form.addRow("Translation key", self.translation_key)
        form.addRow("Author", self.author)
        form.addRow("Blog URL", self.blog_url)
        form.addRow("Title", self.title)
        form.addRow("Description", self.description)
        form.addRow("Slug", self.slug)
        form.addRow("Tags (comma-separated)", self.tags)
        form.addRow("Category", self.category)
        form.addRow("Keywords (comma-separated)", self.keywords)
        form.addRow("Content (EN)", self.content)
        form.addRow("Link policy", self.link_policy)
        form.addRow("", self.default_affiliate_disclosure)
        form.addRow("", self.affiliate_enabled)
        form.addRow("Affiliate URL", self.affiliate_url)
        form.addRow("Affiliate disclosure", self.affiliate_disclosure)

        buttons = QHBoxLayout()
        buttons.addWidget(self.load_draft_button)
        buttons.addWidget(self.save_draft_button)
        buttons.addWidget(self.export_button)
        buttons.addStretch(1)
        form.addRow(buttons)
        group.setLayout(form)
        return group

    def _build_theme_page(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("Choose or Generate a Theme")
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        form = QFormLayout()
        form.addRow("Theme", self.theme_input)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addWidget(self.theme_next_button)
        buttons.addWidget(self.theme_create_button)
        buttons.addWidget(self.theme_import_button)
        buttons.addWidget(self.theme_save_draft_button)
        buttons.addWidget(self.theme_load_draft_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        layout.addWidget(QLabel("Latest blog themes (EN)"))
        self.latest_themes_list.setMinimumHeight(200)
        layout.addWidget(self.latest_themes_list)
        copy_row = QHBoxLayout()
        copy_row.addWidget(self.copy_latest_themes_button)
        copy_row.addStretch(1)
        layout.addLayout(copy_row)

        layout.addStretch(1)
        return container

    def _handle_theme_next(self) -> None:
        theme = self.theme_input.text().strip()
        if not theme:
            QMessageBox.warning(self, "Missing", "Theme is required to continue.")
            return
        self.theme.setText(theme)
        self.stack.setCurrentIndex(1)
        self._set_step(1)

    def _open_create_theme_dialog(self) -> None:
        dialog = ThemeGeneratorDialog(self, self._theme_state, self._latest_themes)
        dialog.theme_selected.connect(self._set_theme_from_dialog)
        dialog.latest_themes_requested.connect(self._handle_import_latest_themes)
        self._theme_dialog = dialog
        dialog.exec()
        self._theme_state = dialog.export_state()
        self._theme_dialog = None
        self._schedule_theme_autosave()

    def _set_theme_from_dialog(self, theme: str) -> None:
        if not theme:
            return
        self.theme_input.setText(theme)
        self.theme.setText(theme)
        self._set_step(1)

    def _handle_import_latest_themes(self) -> None:
        themes = load_latest_blog_themes(limit=20)
        if not themes:
            QMessageBox.warning(self, "No themes", "No recent themes were found.")
            return
        self._latest_themes = [theme.__dict__ for theme in themes]
        self._set_latest_themes(self._latest_themes)
        if self._theme_dialog:
            self._theme_dialog.update_latest_themes(self._latest_themes)
            self._theme_dialog._apply_latest_to_avoid()
        self._schedule_theme_autosave()

    def _set_latest_themes(self, themes: list[dict]) -> None:
        self.latest_themes_list.clear()
        for theme in themes:
            title = theme.get("title", "")
            date_value = theme.get("date", "")
            translation_key = theme.get("translation_key", "")
            label = title
            if date_value:
                label = f"{label} ({date_value})"
            if translation_key:
                label = f"{label} [{translation_key}]"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, title)
            self.latest_themes_list.addItem(item)

    def _copy_latest_themes(self) -> None:
        titles = [item.get("title", "") for item in self._latest_themes if item.get("title")]
        if not titles:
            QMessageBox.information(self, "Empty", "No themes to copy yet.")
            return
        QGuiApplication.clipboard().setText("\n".join(titles))
        QMessageBox.information(self, "Copied", "Copied latest themes to clipboard.")

    def _handle_latest_theme_clicked(self, item: QListWidgetItem) -> None:
        title = item.data(Qt.UserRole)
        if not title:
            return
        QGuiApplication.clipboard().setText(title)
        if title not in self._theme_state.get("avoid_topics", ""):
            avoid = self._theme_state.get("avoid_topics", "")
            self._theme_state["avoid_topics"] = (avoid + "\n" + title).strip()
            if self._theme_dialog:
                self._theme_dialog.avoid_topics.setPlainText(self._theme_state["avoid_topics"])
        self._schedule_theme_autosave()
        QMessageBox.information(self, "Copied", "Theme copied to clipboard.")

    def _schedule_theme_autosave(self) -> None:
        self._theme_autosave_timer.start(800)

    def _autosave_theme_draft(self) -> None:
        self._save_theme_draft(silent=True)

    def _theme_draft_payload(self) -> dict:
        return {
            "theme": self.theme_input.text().strip(),
            "latest_themes": self._latest_themes,
            "niche_context": self._theme_state.get("niche_context", ""),
            "target_audience": self._theme_state.get("target_audience", ""),
            "monetization_constraints": self._theme_state.get("monetization_constraints", ""),
            "constraints": self._theme_state.get("constraints", ""),
            "avoid_topics": self._theme_state.get("avoid_topics", ""),
            "prompt": self._theme_state.get("prompt", ""),
            "pasted_results": self._theme_state.get("pasted_results", ""),
            "suggested_themes": self._theme_state.get("suggested_themes", [])
        }

    def _save_theme_draft(self, silent: bool = False) -> None:
        draft_dir = get_data_dir() / "drafts"
        draft_dir.mkdir(parents=True, exist_ok=True)
        translation_key = self.translation_key.text().strip()
        if not self._theme_draft_path:
            stamp = translation_key or time.strftime("%Y%m%d-%H%M%S")
            self._theme_draft_path = draft_dir / f"{stamp}-theme.json"
        if save_json(self._theme_draft_path, self._theme_draft_payload()):
            if not silent:
                QMessageBox.information(self, "Saved", f"Draft saved to {self._theme_draft_path}")

    def _load_theme_draft(self) -> None:
        draft_dir = get_data_dir() / "drafts"
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Theme Draft", str(draft_dir), "JSON Files (*.json)"
        )
        if not file_name:
            return
        data = load_json(file_name)
        if not data:
            return
        self.theme_input.setText(data.get("theme", ""))
        self._latest_themes = data.get("latest_themes", []) or []
        self._set_latest_themes(self._latest_themes)
        for key in ["niche_context", "target_audience", "monetization_constraints", "constraints", "avoid_topics", "prompt", "pasted_results", "suggested_themes"]:
            if key in data:
                self._theme_state[key] = data[key]
        self._theme_draft_path = Path(file_name)
        QMessageBox.information(self, "Loaded", f"Draft loaded from {file_name}")

    def _build_stepper(self) -> QHBoxLayout:
        steps = [
            "Theme Generator",
            "Creator (EN)",
            "Translator (PT/ES/IT)",
            "Preview/Edit + Publish",
            "Distribution"
        ]
        layout = QHBoxLayout()
        self._step_buttons: list[QPushButton] = []
        for idx, label in enumerate(steps):
            button = QPushButton(label)
            button.setFlat(True)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _, i=idx: self._go_to_step(i))
            self._step_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)
        return layout

    def _set_step(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for idx, button in enumerate(self._step_buttons):
            if idx == index:
                button.setStyleSheet("font-weight: 600; text-decoration: underline;")
            else:
                button.setStyleSheet("font-weight: 400; text-decoration: none;")

    def _go_to_step(self, index: int) -> None:
        if index < 0 or index >= self.stack.count():
            return
        current = self.stack.currentIndex()
        if index > current and not self._can_advance_from(current):
            return
        self._set_step(index)

    def _can_advance_from(self, current: int) -> bool:
        if current == 0:
            return self._validate_theme_step()
        if current == 1:
            return self._validate_creator_step()
        return True

    def _validate_theme_step(self) -> bool:
        theme = self.theme_input.text().strip()
        if not theme:
            QMessageBox.warning(self, "Missing", "Theme is required to continue.")
            return False
        self.theme.setText(theme)
        return True

    def _validate_creator_step(self) -> bool:
        theme = self.theme.text().strip() or self.theme_input.text().strip()
        if theme:
            self.theme.setText(theme)
        if not self.theme.text().strip():
            QMessageBox.warning(self, "Missing", "Theme is required to continue.")
            return False
        if not self.translation_key.text().strip():
            QMessageBox.warning(self, "Missing", "translationKey is required.")
            return False
        if not self.author.text().strip():
            QMessageBox.warning(self, "Missing", "author is required.")
            return False
        if not validate_blog_url(self.blog_url.text().strip()):
            QMessageBox.warning(self, "Invalid", "blogUrl is invalid.")
            return False
        if not self.title.text().strip() or not self.description.text().strip():
            QMessageBox.warning(self, "Missing", "title/description are required.")
            return False
        if not self.slug.text().strip() or not validate_slug(self.slug.text().strip()):
            QMessageBox.warning(self, "Invalid", "slug must be kebab-case.")
            return False
        if not self.content.toPlainText().strip():
            QMessageBox.warning(self, "Missing", "content is required.")
            return False
        return True

    def _build_placeholder_page(self, title_text: str, index: int) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)
        message = QLabel("Placeholder step. This will be implemented in a future iteration.")
        message.setAlignment(Qt.AlignHCenter)
        layout.addWidget(message)
        layout.addStretch(1)

        nav = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self._go_to_step(max(index - 1, 0)))
        nav.addWidget(back_button)
        nav.addStretch(1)
        if index < 4:
            next_button = QPushButton("Next")
            next_button.clicked.connect(lambda: self._go_to_step(min(index + 1, 4)))
            nav.addWidget(next_button)
        layout.addLayout(nav)
        return container

    def _collect_inputs(self) -> CreatorInputs:
        return CreatorInputs(
            theme=self.theme.text().strip(),
            translation_key=self.translation_key.text().strip(),
            author=self.author.text().strip(),
            blog_url=self.blog_url.text().strip(),
            title=self.title.text().strip(),
            description=self.description.text().strip(),
            slug=self.slug.text().strip(),
            tags=[tag.strip() for tag in self.tags.text().split(",") if tag.strip()],
            category=self.category.text().strip(),
            keywords=[kw.strip() for kw in self.keywords.text().split(",") if kw.strip()],
            affiliate_enabled=self.affiliate_enabled.isChecked(),
            affiliate_url=self.affiliate_url.text().strip(),
            affiliate_disclosure=self.affiliate_disclosure.text().strip(),
            content=self.content.toPlainText().strip(),
            link_policy=self.link_policy.currentText(),
            default_affiliate_disclosure=self.default_affiliate_disclosure.isChecked()
        )

    def _maybe_set_translation_key(self) -> None:
        if not self.translation_key.text().strip():
            value = self.slug.text().strip()
            if value:
                self.translation_key.setText(f"{value}-en")

    def handle_export(self) -> None:
        inputs = self._collect_inputs()
        if not inputs.translation_key:
            QMessageBox.warning(self, "Missing", "translationKey is required")
            return
        if not inputs.author:
            QMessageBox.warning(self, "Missing", "author is required")
            return
        if not validate_blog_url(inputs.blog_url):
            QMessageBox.warning(self, "Invalid", "blogUrl is invalid")
            return
        if not inputs.title or not inputs.description or not inputs.slug or not inputs.content:
            QMessageBox.warning(self, "Missing", "title/description/slug/content are required")
            return
        if not validate_slug(inputs.slug):
            QMessageBox.warning(self, "Invalid", "slug must be kebab-case")
            return

        payload = build_content_package(inputs)
        errors = validate_content_package(payload, self.schema_path)
        if errors:
            QMessageBox.critical(self, "Schema error", "\n".join(errors))
            return

        export_dir = get_outputs_dir() / "content-packages"
        path = export_dir / f"{inputs.translation_key}-creator.json"
        if save_json(path, payload):
            QMessageBox.information(self, "Exported", f"Saved to {path}")
            info(f"Exported creator package to {path}")

    def handle_save_draft(self) -> None:
        inputs = self._collect_inputs()
        if not inputs.translation_key:
            QMessageBox.warning(self, "Missing", "translationKey is required")
            return
        draft_dir = get_data_dir() / "drafts"
        path = draft_dir / f"{inputs.translation_key}-creator.json"
        save_json(path, build_content_package(inputs))

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
        self.author.setText(data.get("global", {}).get("author", ""))
        self.blog_url.setText(data.get("global", {}).get("blogUrl", ""))
        self.theme.setText(data.get("global", {}).get("theme", ""))
        self.link_policy.setCurrentText(data.get("global", {}).get("linkPolicy", "no-links"))
        self.default_affiliate_disclosure.setChecked(
            data.get("global", {}).get("defaultAffiliateDisclosure", False)
        )
        en = data.get("locales", {}).get("en", {})
        self.title.setText(en.get("title", ""))
        self.description.setText(en.get("description", ""))
        self.slug.setText(en.get("slug", ""))
        self.content.setPlainText(en.get("content", ""))
        self.tags.setText(", ".join(en.get("tags", []) or []))
        self.category.setText(en.get("category", ""))
        self.keywords.setText(", ".join(en.get("keywords", []) or []))
        affiliate = en.get("affiliate", {})
        self.affiliate_enabled.setChecked(affiliate.get("enabled", False))
        self.affiliate_url.setText(affiliate.get("url", ""))
        self.affiliate_disclosure.setText(affiliate.get("disclosure", ""))


class ThemeGeneratorDialog(QDialog):
    theme_selected = Signal(str)
    latest_themes_requested = Signal()

    def __init__(self, parent: QWidget, state: dict, latest_themes: list[dict]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create Theme")
        self.resize(900, 700)
        self._latest_themes = latest_themes

        self.niche_context = QLineEdit(state.get("niche_context", ""))
        self.target_audience = QLineEdit(state.get("target_audience", ""))
        self.monetization_constraints = QLineEdit(state.get("monetization_constraints", ""))
        self.constraints = QLineEdit(state.get("constraints", ""))
        self.avoid_topics = QPlainTextEdit(state.get("avoid_topics", ""))

        self.prompt_output = QPlainTextEdit(state.get("prompt", ""))
        self.prompt_output.setReadOnly(True)
        self.paste_results = QPlainTextEdit(state.get("pasted_results", ""))
        self.suggestions_list = QListWidget()

        for suggestion in state.get("suggested_themes", []) or []:
            item = QListWidgetItem(suggestion)
            item.setData(Qt.UserRole, suggestion)
            self.suggestions_list.addItem(item)

        self.generate_button = QPushButton("Generate Perplexity prompt")
        self.generate_button.clicked.connect(self._generate_prompt)
        self.copy_prompt_button = QPushButton("Copy prompt")
        self.copy_prompt_button.clicked.connect(self._copy_prompt)
        self.import_latest_button = QPushButton("Import latest blog themes")
        self.import_latest_button.clicked.connect(self.latest_themes_requested.emit)

        self.parse_button = QPushButton("Parse ideas")
        self.parse_button.clicked.connect(self._parse_results)

        self.suggestions_list.itemClicked.connect(self._handle_suggestion_click)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("Niche context", self.niche_context)
        form.addRow("Target audience", self.target_audience)
        form.addRow("Monetization constraints", self.monetization_constraints)
        form.addRow("Constraints", self.constraints)
        form.addRow("Avoid these topics", self.avoid_topics)
        layout.addLayout(form)

        prompt_row = QHBoxLayout()
        prompt_row.addWidget(self.generate_button)
        prompt_row.addWidget(self.copy_prompt_button)
        prompt_row.addWidget(self.import_latest_button)
        prompt_row.addStretch(1)
        layout.addLayout(prompt_row)

        layout.addWidget(QLabel("Prompt to Perplexity"))
        layout.addWidget(self.prompt_output)

        layout.addWidget(QLabel("Paste Perplexity results"))
        layout.addWidget(self.paste_results)
        layout.addWidget(self.parse_button)

        layout.addWidget(QLabel("Suggested themes"))
        layout.addWidget(self.suggestions_list)

    def export_state(self) -> dict:
        return {
            "niche_context": self.niche_context.text().strip(),
            "target_audience": self.target_audience.text().strip(),
            "monetization_constraints": self.monetization_constraints.text().strip(),
            "constraints": self.constraints.text().strip(),
            "avoid_topics": self.avoid_topics.toPlainText().strip(),
            "prompt": self.prompt_output.toPlainText(),
            "pasted_results": self.paste_results.toPlainText(),
            "suggested_themes": [self.suggestions_list.item(i).text() for i in range(self.suggestions_list.count())]
        }

    def update_latest_themes(self, latest_themes: list[dict]) -> None:
        self._latest_themes = latest_themes

    def _apply_latest_to_avoid(self) -> None:
        if not self._latest_themes:
            return
        titles = [theme.get("title", "") for theme in self._latest_themes if theme.get("title")]
        if not titles:
            return
        current = self.avoid_topics.toPlainText().strip()
        combined = "\n".join([current] + titles if current else titles)
        self.avoid_topics.setPlainText(combined.strip())

    def _generate_prompt(self) -> None:
        avoid = self.avoid_topics.toPlainText().strip()
        avoid_block = f"\nAvoid these recent themes:\n{avoid}\n" if avoid else ""
        prompt = (
            "You are a content strategist. Return a JSON response with 20-30 topic ideas grouped by cluster.\n"
            "Scope: today’s best topics for the niche and audience below.\n"
            "Each topic must include: topic_title, why_it_will_work, target_keywords, content_angle, "
            "recommended_infoproduct_type (course/coaching/template), estimated_evergreen_score (1-10), "
            "competition_risk (low/med/high).\n"
            "Also include a short rationale per cluster.\n\n"
            f"Niche context: {self.niche_context.text().strip()}\n"
            f"Target audience: {self.target_audience.text().strip()}\n"
            f"Monetization constraints: {self.monetization_constraints.text().strip()}\n"
            f"Constraints: {self.constraints.text().strip()}\n"
            f"{avoid_block}"
        )
        self.prompt_output.setPlainText(prompt.strip())

    def _copy_prompt(self) -> None:
        text = self.prompt_output.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Empty", "Generate a prompt first.")
            return
        QGuiApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Prompt copied to clipboard.")

    def _parse_results(self) -> None:
        raw = self.paste_results.toPlainText().strip()
        if not raw:
            QMessageBox.warning(self, "Empty", "Paste results first.")
            return
        suggestions: list[str] = []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                for key in ["topics", "items", "ideas", "clusters"]:
                    if key in parsed:
                        parsed = parsed[key]
                        break
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        title = item.get("topic_title") or item.get("title") or ""
                        if title:
                            suggestions.append(title.strip())
                    elif isinstance(item, str):
                        suggestions.append(item.strip())
        except Exception:
            pass

        if not suggestions:
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("-", "*")):
                    suggestions.append(line.lstrip("-* ").strip())
                    continue
                if line[0].isdigit() and "." in line[:3]:
                    suggestions.append(line.split(".", 1)[1].strip())

        if not suggestions:
            QMessageBox.warning(self, "Parse failed", "Could not parse suggestions.")
            return

        self.suggestions_list.clear()
        for suggestion in suggestions:
            item = QListWidgetItem(suggestion)
            item.setData(Qt.UserRole, suggestion)
            self.suggestions_list.addItem(item)

    def _handle_suggestion_click(self, item: QListWidgetItem) -> None:
        title = item.data(Qt.UserRole)
        if not title:
            return
        self.theme_selected.emit(title)
        self.accept()
