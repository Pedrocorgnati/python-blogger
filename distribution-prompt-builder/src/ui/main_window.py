from __future__ import annotations

from typing import Dict, List
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
from PySide6.QtCore import QTimer

from core.channel_rules import CHANNEL_RULES
from core.models import AffiliateLinks, GlobalInputs, LocaleContent, PromptResult
from core.prompt_generator import generate_prompts
from profile_kit.bio_generator import build_bio_generation_prompt, build_bio_generation_prompt_all
from profile_kit.bio_loader import default_bio_kit, load_bio_kit
from profile_kit.bio_models import BIO_FIELDS, CHANNELS, LOCALES, BioKit
from profile_kit.bio_storage import save_bios_json, save_bios_md, save_runtime_copy
from utils.clipboard import copy_to_clipboard
from utils.io import save_all_prompts, save_per_channel, save_results_templates, load_content_package
from utils.logger import info, warn, error
from utils.paths import (
    ensure_app_dirs,
    get_app_root,
    get_data_dir,
    get_outputs_dir,
    get_repo_schema_path
)
from utils.validators import infer_title_from_content, validate_inputs, validate_blog_url, validate_slug


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("distribution-prompt-builder")
        self.resize(1200, 860)

        self.outputs_dir = get_outputs_dir() / "distribution-prompts"
        self.profile_data_path = get_data_dir() / "profiles.json"
        self.profile_json_path = get_app_root() / "profile-kit" / "bios.json"
        self.profile_md_path = get_app_root() / "profile-kit" / "bios.md"
        self.profile_export_dir = get_outputs_dir() / "profile-kit"
        self.schema_path = get_repo_schema_path()

        ensure_app_dirs()
        (get_app_root() / "profile-kit").mkdir(parents=True, exist_ok=True)

        self.bio_kit: BioKit = load_bio_kit(self.profile_data_path)
        if not self.profile_data_path.exists():
            save_runtime_copy(self.profile_data_path, self.bio_kit)

        self.translation_key = QLineEdit()
        self.author = QLineEdit()
        self.affiliate_disclosure = QCheckBox("Affiliate disclosure enabled")
        self.blog_url = QLineEdit()
        self.post_slug_en = QLineEdit()
        self.post_slug_pt = QLineEdit()
        self.post_slug_es = QLineEdit()
        self.post_slug_it = QLineEdit()

        self.main_cta = QComboBox()
        self.main_cta.addItems([
            "Reputation only (no selling)",
            "Soft traffic to blog"
        ])

        self.link_policy = QComboBox()
        self.link_policy.addItems([
            "No links",
            "Blog link only",
            "Blog link + optional affiliate link (non-Reddit/Quora only)"
        ])

        self.affiliate_override = QCheckBox("Allow affiliate link override for Reddit/Quora")
        self.import_button = QPushButton("Import Content Package (JSON)")
        self.import_button.clicked.connect(self.handle_import_package)

        self.distribution_mode_group = QButtonGroup()
        self.distribution_single = QRadioButton("Single account (all languages)")
        self.distribution_separate = QRadioButton("Separate accounts per language")
        self.distribution_separate.setChecked(True)
        self.distribution_mode_group.addButton(self.distribution_single)
        self.distribution_mode_group.addButton(self.distribution_separate)

        self.affiliate_en = QLineEdit()
        self.affiliate_pt = QLineEdit()
        self.affiliate_es = QLineEdit()
        self.affiliate_it = QLineEdit()

        self.tone = QLineEdit("professional, direct, helpful, not hypey")
        self.persona = QLineEdit("experienced tech mentor")

        self.length = QComboBox()
        self.length.addItems(["Short", "Standard", "Long"])

        self.generate_variants = QCheckBox("Generate 2 variants per channel")
        self.generate_variants.setChecked(True)

        self.include_comments = QCheckBox("Include comment templates")
        self.include_comments.setChecked(True)

        self.linkedin_generate_comment = QCheckBox("Generate first comment")
        self.linkedin_generate_comment.setChecked(True)
        self.linkedin_cta_policy = QComboBox()
        self.linkedin_cta_policy.addItems(["No links", "Link in comments", "Link at end of post"])

        self.channel_checks: Dict[str, QCheckBox] = {}

        self.locale_tabs = QTabWidget()
        self.locale_inputs: Dict[str, Dict[str, QTextEdit | QLineEdit]] = {}
        self.locale_meta: Dict[str, Dict[str, object]] = {}
        self._setup_locale_tabs()


        self.generate_button = QPushButton("Generate posts")
        self.generate_button.clicked.connect(self.handle_generate)
        self.save_draft_button = QPushButton("Save Draft")
        self.save_draft_button.clicked.connect(self.handle_save_draft)
        self.load_draft_button = QPushButton("Load Draft")
        self.load_draft_button.clicked.connect(self.handle_load_draft)

        self.copy_button = QPushButton("Copy everything")
        self.copy_button.clicked.connect(self.handle_copy)

        self.save_button = QPushButton("Save all")
        self.save_button.clicked.connect(self.handle_save_all)

        self.save_per_channel_button = QPushButton("Save to file (per channel)")
        self.save_per_channel_button.clicked.connect(self.handle_save_per_channel)

        layout = QVBoxLayout()
        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(self._build_distribution_tab(), "Distribution")
        self.main_tabs.addTab(self._build_profile_tab(), "Profiles & Bios")
        layout.addWidget(self.main_tabs)
        self.setLayout(layout)

        self._last_prompts = []
        self._bundle_by_channel: Dict[str, str] = {}
        self._channel_outputs: Dict[str, Dict[str, QTextEdit]] = {}
        self._last_global_inputs: GlobalInputs | None = None
        self._loading_profile = False

    def _build_distribution_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self._build_form())
        layout.addWidget(self._build_output())
        return container

    def _build_form(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self._build_global_group())
        layout.addWidget(self._build_affiliate_group())
        layout.addWidget(self._build_content_group())
        layout.addWidget(self._build_channels_group())
        layout.addWidget(self._build_style_group())

        button_row = QHBoxLayout()
        button_row.addWidget(self.load_draft_button)
        button_row.addWidget(self.save_draft_button)
        button_row.addWidget(self.generate_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        return scroll

    def _build_global_group(self) -> QWidget:
        group = QGroupBox("Global inputs")
        form = QFormLayout()
        form.addRow("Translation key", self.translation_key)
        form.addRow("Author", self.author)
        form.addRow("Blog URL", self.blog_url)
        form.addRow("Post slug EN", self.post_slug_en)
        form.addRow("Post slug PT", self.post_slug_pt)
        form.addRow("Post slug ES", self.post_slug_es)
        form.addRow("Post slug IT", self.post_slug_it)
        form.addRow("Main call to action", self.main_cta)
        form.addRow("Link policy", self.link_policy)
        form.addRow("", self.affiliate_disclosure)
        form.addRow("", self.affiliate_override)
        form.addRow("", self.import_button)
        form.addRow("Distribution plan", self._build_distribution_plan())
        group.setLayout(form)
        return group

    def _build_distribution_plan(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.distribution_single)
        layout.addWidget(self.distribution_separate)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def _build_affiliate_group(self) -> QWidget:
        group = QGroupBox("Affiliate links (optional)")
        form = QFormLayout()
        form.addRow("Affiliate EN", self.affiliate_en)
        form.addRow("Affiliate PT", self.affiliate_pt)
        form.addRow("Affiliate ES", self.affiliate_es)
        form.addRow("Affiliate IT", self.affiliate_it)
        group.setLayout(form)
        return group

    def _build_content_group(self) -> QWidget:
        group = QGroupBox("Article content by locale")
        layout = QVBoxLayout()
        layout.addWidget(self.locale_tabs)
        group.setLayout(layout)
        return group

    def _setup_locale_tabs(self) -> None:
        for locale in ["en", "pt", "es", "it"]:
            tab = QWidget()
            form = QFormLayout(tab)
            title_input = QLineEdit()
            description_input = QLineEdit()
            content_input = QTextEdit()
            content_input.setMinimumHeight(220)

            self.locale_inputs[locale] = {
                "title": title_input,
                "description": description_input,
                "content": content_input
            }
            self.locale_meta[locale] = {"tags": [], "category": "", "keywords": []}

            form.addRow("Title", title_input)
            form.addRow("Description", description_input)
            form.addRow("Content", content_input)
            self.locale_tabs.addTab(tab, locale.upper())

    def _build_channels_group(self) -> QWidget:
        group = QGroupBox("Channels")
        grid = QGridLayout()
        row = 0
        col = 0
        for name in CHANNEL_RULES.keys():
            checkbox = QCheckBox(name)
            self.channel_checks[name] = checkbox
            grid.addWidget(checkbox, row, col)
            col += 1
            if col > 2:
                row += 1
                col = 0
        group.setLayout(grid)
        return group

    def _build_style_group(self) -> QWidget:
        group = QGroupBox("Style settings")
        form = QFormLayout()
        form.addRow("Tone", self.tone)
        form.addRow("Persona", self.persona)
        form.addRow("Length", self.length)
        form.addRow("", self.generate_variants)
        form.addRow("", self.include_comments)
        form.addRow("LinkedIn options", self._build_linkedin_options())
        group.setLayout(form)
        return group

    def _build_linkedin_options(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.linkedin_generate_comment)
        layout.addWidget(self.linkedin_cta_policy)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

    def _build_output(self) -> QWidget:
        group = QGroupBox("Generated prompts")
        layout = QVBoxLayout()
        self.output_tabs = QTabWidget()
        layout.addWidget(self.output_tabs)

        buttons = QHBoxLayout()
        buttons.addWidget(self.copy_button)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.save_per_channel_button)
        buttons.addStretch(1)

        layout.addLayout(buttons)
        group.setLayout(layout)
        return group

    def _build_profile_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        selection_group = QGroupBox("Profile selection")
        selection_layout = QFormLayout()
        self.profile_locale = QComboBox()
        self.profile_locale.addItems([loc.upper() for loc in LOCALES])
        self.profile_channel = QComboBox()
        self.profile_channel.addItems(CHANNELS)
        selection_layout.addRow("Locale", self.profile_locale)
        selection_layout.addRow("Channel", self.profile_channel)
        selection_group.setLayout(selection_layout)

        bio_group = QGroupBox("Bio fields")
        bio_layout = QFormLayout()
        self.bio_fields: Dict[str, QTextEdit] = {}
        for field in BIO_FIELDS:
            editor = QTextEdit()
            editor.setMinimumHeight(60)
            editor.textChanged.connect(self._update_profile_preview)
            self.bio_fields[field] = editor
            bio_layout.addRow(field.replace("_", " ").title(), editor)
        bio_group.setLayout(bio_layout)

        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        self.profile_preview = QTextEdit()
        self.profile_preview.setReadOnly(True)
        preview_layout.addWidget(self.profile_preview)
        preview_group.setLayout(preview_layout)

        actions = QHBoxLayout()
        self.generate_bio_lang = QPushButton("Generate Bio Kit (this language)")
        self.generate_bio_lang.clicked.connect(self._generate_bio_prompt_language)
        self.generate_bio_all = QPushButton("Generate Bio Kit (all languages)")
        self.generate_bio_all.clicked.connect(self._generate_bio_prompt_all)
        self.save_bio = QPushButton("Save")
        self.save_bio.clicked.connect(self._save_bio_kit)
        self.reset_bio = QPushButton("Reset to default")
        self.reset_bio.clicked.connect(self._reset_bio_kit)
        self.export_json = QPushButton("Export Profile Kit (JSON)")
        self.export_json.clicked.connect(self._export_profile_json)
        self.export_md = QPushButton("Export Profile Kit (MD)")
        self.export_md.clicked.connect(self._export_profile_md)
        actions.addWidget(self.generate_bio_lang)
        actions.addWidget(self.generate_bio_all)
        actions.addWidget(self.save_bio)
        actions.addWidget(self.reset_bio)
        actions.addWidget(self.export_json)
        actions.addWidget(self.export_md)
        actions.addStretch(1)

        prompt_group = QGroupBox("Bio Kit prompt (copy to GPT)")
        prompt_layout = QVBoxLayout()
        self.bio_prompt_output = QTextEdit()
        self.bio_prompt_output.setReadOnly(True)
        prompt_layout.addWidget(self.bio_prompt_output)
        prompt_group.setLayout(prompt_layout)

        self.profile_status = QLabel("Saved")

        layout.addWidget(selection_group)
        layout.addWidget(bio_group)
        layout.addWidget(preview_group)
        layout.addLayout(actions)
        layout.addWidget(self.profile_status)
        layout.addWidget(prompt_group)

        self.profile_locale.currentTextChanged.connect(self._load_profile_fields)
        self.profile_channel.currentTextChanged.connect(self._load_profile_fields)
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._autosave_profile_kit)
        self._load_profile_fields()

        return container

    def _collect_global_inputs(self) -> GlobalInputs:
        return GlobalInputs(
            translation_key=self.translation_key.text().strip(),
            author=self.author.text().strip(),
            affiliate_disclosure=self.affiliate_disclosure.isChecked(),
            blog_url=self.blog_url.text().strip(),
            post_slug_en=self.post_slug_en.text().strip(),
            post_slug_pt=self.post_slug_pt.text().strip(),
            post_slug_es=self.post_slug_es.text().strip(),
            post_slug_it=self.post_slug_it.text().strip(),
            main_call_to_action=self.main_cta.currentText(),
            link_policy=self.link_policy.currentText(),
            tone=self.tone.text().strip(),
            persona=self.persona.text().strip(),
            length=self.length.currentText().lower(),
            generate_variants=self.generate_variants.isChecked(),
            include_comment_templates=self.include_comments.isChecked(),
            allow_affiliate_override=self.affiliate_override.isChecked(),
            distribution_mode="separate" if self.distribution_separate.isChecked() else "single",
            linkedin_generate_comment=self.linkedin_generate_comment.isChecked(),
            linkedin_cta_policy=self.linkedin_cta_policy.currentText()
        )

    def _collect_affiliate_links(self) -> AffiliateLinks:
        return AffiliateLinks(
            en=self.affiliate_en.text().strip(),
            pt=self.affiliate_pt.text().strip(),
            es=self.affiliate_es.text().strip(),
            it=self.affiliate_it.text().strip()
        )

    def _collect_locale_contents(self) -> Dict[str, LocaleContent]:
        contents: Dict[str, LocaleContent] = {}
        for locale, inputs in self.locale_inputs.items():
            title = inputs["title"].text().strip() if isinstance(inputs["title"], QLineEdit) else ""
            description = (
                inputs["description"].text().strip() if isinstance(inputs["description"], QLineEdit) else ""
            )
            content = inputs["content"].toPlainText().strip() if isinstance(inputs["content"], QTextEdit) else ""

            if not title and content:
                inferred = infer_title_from_content(content)
                if inferred:
                    title = inferred

            contents[locale] = LocaleContent(
                locale=locale,
                title=title,
                description=description,
                content=content,
                tags=self.locale_meta.get(locale, {}).get("tags", []),
                category=str(self.locale_meta.get(locale, {}).get("category", "")),
                keywords=self.locale_meta.get(locale, {}).get("keywords", [])
            )
        return contents

    def _selected_channels(self) -> List[str]:
        return [name for name, checkbox in self.channel_checks.items() if checkbox.isChecked()]

    def handle_generate(self) -> None:
        global_inputs = self._collect_global_inputs()
        locale_contents = self._collect_locale_contents()
        channels = self._selected_channels()

        issues = validate_inputs(global_inputs, list(locale_contents.values()), channels)
        if issues:
            QMessageBox.warning(self, "Missing info", "\n".join(issues))
            return
        if not validate_blog_url(global_inputs.blog_url):
            QMessageBox.warning(self, "Invalid URL", "Blog URL is invalid.")
            return
        invalid_slugs = []
        required_slugs = {
            "EN": global_inputs.post_slug_en,
            "PT": global_inputs.post_slug_pt or global_inputs.post_slug_en,
            "ES": global_inputs.post_slug_es or global_inputs.post_slug_en,
            "IT": global_inputs.post_slug_it or global_inputs.post_slug_en
        }
        for label, slug in required_slugs.items():
            if not slug or not validate_slug(slug):
                invalid_slugs.append(label)
        if invalid_slugs:
            QMessageBox.warning(self, "Invalid slug", f"Invalid slug(s): {', '.join(invalid_slugs)}")
            return

        if global_inputs.distribution_mode == "separate":
            missing_locales = [
                locale for locale, item in locale_contents.items() if not item.content.strip()
            ]
            if missing_locales:
                QMessageBox.critical(
                    self,
                    "Missing locales",
                    "Separate accounts mode expects all locales. Missing content: "
                    + ", ".join([loc.upper() for loc in missing_locales])
                )
                return
            missing_descriptions = [
                locale for locale, item in locale_contents.items() if not item.description.strip()
            ]
            if missing_descriptions:
                QMessageBox.critical(
                    self,
                    "Missing descriptions",
                    "Descriptions are required for all locales: "
                    + ", ".join([loc.upper() for loc in missing_descriptions])
                )
                return

        bundle_by_channel, prompts = generate_prompts(
            global_inputs,
            locale_contents,
            self._collect_affiliate_links(),
            channels,
            self.bio_kit
        )
        if not prompts:
            QMessageBox.warning(self, "No prompts", "No prompts were generated. Check content fields.")
            return

        self._last_prompts = prompts
        self._bundle_by_channel = bundle_by_channel
        self._last_global_inputs = global_inputs
        self._render_outputs(channels, locale_contents)
        info("Prompts generated.")

        missing_titles = [
            locale for locale, item in locale_contents.items() if not item.title and item.content
        ]
        if missing_titles:
            QMessageBox.information(
                self,
                "Title inferred",
                "Some titles were inferred from content: " + ", ".join(missing_titles)
            )

    def handle_copy(self) -> None:
        if not self._last_prompts:
            QMessageBox.warning(self, "No prompts", "Generate prompts first.")
            return
        global_inputs = self._collect_global_inputs()
        if global_inputs.distribution_mode == "separate":
            full_text = "\n\n".join(self._bundle_by_channel.values())
        else:
            full_text = "\n\n".join([item.prompt_text for item in self._last_prompts])
        copy_to_clipboard(full_text)

    def handle_save_all(self) -> None:
        if not self._last_prompts:
            QMessageBox.warning(self, "No prompts", "Generate prompts first.")
            return
        global_inputs = self._collect_global_inputs()
        if global_inputs.distribution_mode == "separate":
            bundle_results = [
                PromptResult(channel=channel, locale="bundle", variant="A", prompt_text=text)
                for channel, text in self._bundle_by_channel.items()
            ]
            path = save_all_prompts(self.outputs_dir, global_inputs.translation_key, bundle_results)
        else:
            path = save_all_prompts(self.outputs_dir, global_inputs.translation_key, self._last_prompts)
        save_results_templates(
            get_outputs_dir() / "distribution-results",
            global_inputs.translation_key,
            self._selected_channels()
        )
        QMessageBox.information(self, "Saved", f"Saved to {path}")

    def handle_save_per_channel(self) -> None:
        if not self._last_prompts:
            QMessageBox.warning(self, "No prompts", "Generate prompts first.")
            return
        global_inputs = self._collect_global_inputs()
        paths = save_per_channel(self.outputs_dir, global_inputs.translation_key, self._bundle_by_channel)
        save_results_templates(
            get_outputs_dir() / "distribution-results",
            global_inputs.translation_key,
            self._selected_channels()
        )
        QMessageBox.information(self, "Saved", "Saved files:\n" + "\n".join(paths))

    def handle_save_draft(self) -> None:
        global_inputs = self._collect_global_inputs()
        if not global_inputs.translation_key:
            QMessageBox.warning(self, "Missing key", "Translation key is required to save a draft.")
            return
        data = {
            "global": {
                "translationKey": global_inputs.translation_key,
                "author": global_inputs.author,
                "blogUrl": global_inputs.blog_url,
                "postSlugs": {
                    "en": global_inputs.post_slug_en,
                    "pt": global_inputs.post_slug_pt,
                    "es": global_inputs.post_slug_es,
                    "it": global_inputs.post_slug_it
                },
                "linkPolicy": global_inputs.link_policy,
                "affiliateDisclosure": global_inputs.affiliate_disclosure,
                "distributionMode": global_inputs.distribution_mode,
                "linkedinGenerateComment": global_inputs.linkedin_generate_comment,
                "linkedinCtaPolicy": global_inputs.linkedin_cta_policy,
                "tone": global_inputs.tone,
                "persona": global_inputs.persona,
                "length": global_inputs.length
            },
            "affiliate": {
                "en": self.affiliate_en.text().strip(),
                "pt": self.affiliate_pt.text().strip(),
                "es": self.affiliate_es.text().strip(),
                "it": self.affiliate_it.text().strip()
            },
            "channels": self._selected_channels(),
            "locales": {
                locale: {
                    "title": self.locale_inputs[locale]["title"].text(),
                    "description": self.locale_inputs[locale]["description"].text(),
                    "content": self.locale_inputs[locale]["content"].toPlainText(),
                    "tags": self.locale_meta[locale]["tags"],
                    "category": self.locale_meta[locale]["category"],
                    "keywords": self.locale_meta[locale]["keywords"]
                }
                for locale in ["en", "pt", "es", "it"]
            }
        }
        draft_dir = get_data_dir() / "drafts"
        draft_dir.mkdir(parents=True, exist_ok=True)
        path = draft_dir / f"{global_inputs.translation_key}-distributor.json"
        try:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)
            info(f"Draft saved to {path}")
            QMessageBox.information(self, "Saved", f"Draft saved to {path}")
        except Exception as exc:
            error(f"Failed to save draft to {path}: {exc}")
            QMessageBox.critical(self, "Save error", f"Failed to save draft: {exc}")

    def handle_load_draft(self) -> None:
        draft_dir = get_data_dir() / "drafts"
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Draft", str(draft_dir), "JSON Files (*.json)"
        )
        if not file_name:
            return
        target = Path(file_name)
        try:
            with target.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            error(f"Failed to load draft from {target}: {exc}")
            QMessageBox.critical(self, "Load error", f"Failed to load draft: {exc}")
            return

        global_data = data.get("global", {})
        self.translation_key.setText(global_data.get("translationKey", ""))
        self.author.setText(global_data.get("author", ""))
        self.blog_url.setText(global_data.get("blogUrl", ""))
        slugs = global_data.get("postSlugs", {})
        self.post_slug_en.setText(slugs.get("en", ""))
        self.post_slug_pt.setText(slugs.get("pt", ""))
        self.post_slug_es.setText(slugs.get("es", ""))
        self.post_slug_it.setText(slugs.get("it", ""))
        self.link_policy.setCurrentText(global_data.get("linkPolicy", "No links"))
        self.affiliate_disclosure.setChecked(global_data.get("affiliateDisclosure", False))
        self.tone.setText(global_data.get("tone", self.tone.text()))
        self.persona.setText(global_data.get("persona", self.persona.text()))
        self.length.setCurrentText(global_data.get("length", "standard").capitalize())
        self.linkedin_generate_comment.setChecked(global_data.get("linkedinGenerateComment", True))
        self.linkedin_cta_policy.setCurrentText(global_data.get("linkedinCtaPolicy", "Link in comments"))

        if global_data.get("distributionMode") == "single":
            self.distribution_single.setChecked(True)
        else:
            self.distribution_separate.setChecked(True)

        affiliate = data.get("affiliate", {})
        self.affiliate_en.setText(affiliate.get("en", ""))
        self.affiliate_pt.setText(affiliate.get("pt", ""))
        self.affiliate_es.setText(affiliate.get("es", ""))
        self.affiliate_it.setText(affiliate.get("it", ""))

        locales = data.get("locales", {})
        for locale in ["en", "pt", "es", "it"]:
            loc = locales.get(locale, {})
            self.locale_inputs[locale]["title"].setText(loc.get("title", ""))
            self.locale_inputs[locale]["description"].setText(loc.get("description", ""))
            self.locale_inputs[locale]["content"].setPlainText(loc.get("content", ""))
            self.locale_meta[locale]["tags"] = loc.get("tags", []) or []
            self.locale_meta[locale]["category"] = loc.get("category", "") or ""
            self.locale_meta[locale]["keywords"] = loc.get("keywords", []) or []

        channels = data.get("channels", [])
        for name, checkbox in self.channel_checks.items():
            checkbox.setChecked(name in channels)
        info(f"Draft loaded from {file_name}")

    def _render_outputs(self, channels: List[str], locale_contents: Dict[str, LocaleContent]) -> None:
        self.output_tabs.clear()
        self._channel_outputs.clear()
        locales = ["en", "pt", "es", "it"]

        for channel in channels:
            channel_tab = QWidget()
            channel_layout = QVBoxLayout(channel_tab)
            locale_tabs = QTabWidget()
            self._channel_outputs[channel] = {}

            for locale in locales:
                locale_tab = QWidget()
                locale_layout = QVBoxLayout(locale_tab)
                text_area = QTextEdit()
                text_area.setReadOnly(True)
                prompt = self._resolve_prompt_text(channel, locale)
                text_area.setPlainText(prompt)
                locale_layout.addWidget(text_area)

                button_row = QHBoxLayout()
                copy_button = QPushButton("Copy this")
                copy_button.clicked.connect(lambda _, t=text_area: copy_to_clipboard(t.toPlainText()))
                channel_copy = QPushButton("Copy all for this channel")
                channel_copy.clicked.connect(
                    lambda _, c=channel: copy_to_clipboard(self._bundle_by_channel.get(c, ""))
                )
                button_row.addWidget(copy_button)
                button_row.addWidget(channel_copy)
                button_row.addStretch(1)
                locale_layout.addLayout(button_row)

                locale_tabs.addTab(locale_tab, locale.upper())
                self._channel_outputs[channel][locale] = text_area

            channel_layout.addWidget(locale_tabs)
            channel_actions = QHBoxLayout()
            copy_channel = QPushButton("Copy all for this channel")
            copy_channel.clicked.connect(
                lambda _, c=channel: copy_to_clipboard(self._bundle_by_channel.get(c, ""))
            )
            channel_actions.addWidget(copy_channel)
            channel_actions.addStretch(1)
            channel_layout.addLayout(channel_actions)

            self.output_tabs.addTab(channel_tab, channel)

    def _resolve_prompt_text(self, channel: str, locale: str) -> str:
        if self._last_global_inputs and self._last_global_inputs.distribution_mode == "separate":
            bundle = self._bundle_by_channel.get(channel, "")
            return self._extract_locale_block(bundle, locale, channel)
        return "\n\n".join(
            [
                item.prompt_text
                for item in self._last_prompts
                if item.channel == channel and item.locale == locale
            ]
        )

    def _extract_locale_block(self, bundle: str, locale: str, channel: str) -> str:
        marker = f"=== LOCALE: {locale.upper()} ==="
        if marker not in bundle:
            return bundle
        parts = bundle.split(marker)
        if len(parts) < 2:
            return bundle
        tail = parts[1]
        next_marker = tail.find("=== LOCALE:")
        if next_marker != -1:
            tail = tail[:next_marker]
        header = bundle.split("Return exactly this structure and nothing else:", 1)[0]
        return f"{header.strip()}\nReturn exactly this structure and nothing else:\nCHANNEL: {channel}\n{marker}{tail}"

    def _load_profile_fields(self) -> None:
        locale = self.profile_locale.currentText().lower()
        channel = self.profile_channel.currentText()
        entry = self.bio_kit.profiles.get(locale, {}).get(channel)
        if not entry:
            entry = default_bio_kit().profiles[locale][channel]
            self.bio_kit.profiles.setdefault(locale, {})[channel] = entry
        self._loading_profile = True
        for field in BIO_FIELDS:
            editor = self.bio_fields[field]
            editor.blockSignals(True)
            editor.setPlainText(getattr(entry, field))
            editor.blockSignals(False)
        self._update_profile_preview()
        self._loading_profile = False
        self.profile_status.setText("Saved")

    def _update_profile_preview(self) -> None:
        locale = self.profile_locale.currentText().lower()
        channel = self.profile_channel.currentText()
        entry = self._collect_profile_entry()
        self.bio_kit.profiles.setdefault(locale, {})[channel] = entry
        preview_lines = [
            f"Locale: {locale.upper()}",
            f"Channel: {channel}",
            "",
            f"short_bio: {entry.short_bio}",
            f"medium_bio: {entry.medium_bio}",
            f"long_bio: {entry.long_bio}",
            f"one_liner_tagline: {entry.one_liner_tagline}",
            f"pinned_post_template: {entry.pinned_post_template}",
            f"link_policy_notes: {entry.link_policy_notes}",
            f"dos_and_donts: {entry.dos_and_donts}"
        ]
        self.profile_preview.setPlainText("\n".join(preview_lines))
        if not self._loading_profile:
            self.profile_status.setText("Unsaved changes")
            self._autosave_timer.start(1200)

    def _collect_profile_entry(self):
        from profile_kit.bio_models import BioEntry

        return BioEntry(
            short_bio=self.bio_fields["short_bio"].toPlainText().strip(),
            medium_bio=self.bio_fields["medium_bio"].toPlainText().strip(),
            long_bio=self.bio_fields["long_bio"].toPlainText().strip(),
            one_liner_tagline=self.bio_fields["one_liner_tagline"].toPlainText().strip(),
            pinned_post_template=self.bio_fields["pinned_post_template"].toPlainText().strip(),
            link_policy_notes=self.bio_fields["link_policy_notes"].toPlainText().strip(),
            dos_and_donts=self.bio_fields["dos_and_donts"].toPlainText().strip()
        )

    def _save_bio_kit(self) -> None:
        locale = self.profile_locale.currentText().lower()
        channel = self.profile_channel.currentText()
        entry = self._collect_profile_entry()
        self.bio_kit.profiles.setdefault(locale, {})[channel] = entry
        save_bios_json(self.profile_json_path, self.bio_kit)
        save_bios_md(self.profile_md_path, self.bio_kit)
        save_runtime_copy(self.profile_data_path, self.bio_kit)
        self.profile_status.setText("Saved")
        QMessageBox.information(self, "Saved", "Profile kit saved.")

    def _reset_bio_kit(self) -> None:
        self.bio_kit = default_bio_kit()
        save_runtime_copy(self.profile_data_path, self.bio_kit)
        self._load_profile_fields()
        self.profile_status.setText("Saved")
        QMessageBox.information(self, "Reset", "Profile kit reset to defaults.")

    def _export_profile_json(self) -> None:
        save_bios_json(self.profile_export_dir / "bios.json", self.bio_kit)
        QMessageBox.information(self, "Exported", "Profile kit JSON exported.")

    def _export_profile_md(self) -> None:
        save_bios_md(self.profile_export_dir / "bios.md", self.bio_kit)
        QMessageBox.information(self, "Exported", "Profile kit MD exported.")

    def _generate_bio_prompt_language(self) -> None:
        locale = self.profile_locale.currentText().lower()
        self.bio_prompt_output.setPlainText(build_bio_generation_prompt(locale))

    def _generate_bio_prompt_all(self) -> None:
        self.bio_prompt_output.setPlainText(build_bio_generation_prompt_all())

    def _autosave_profile_kit(self) -> None:
        save_runtime_copy(self.profile_data_path, self.bio_kit)
        self.profile_status.setText("Saved")

    def handle_import_package(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Content Package", "", "JSON Files (*.json)")
        if not file_name:
            return
        data, errors = load_content_package(file_name, self.schema_path)
        if errors:
            QMessageBox.critical(self, "Invalid package", "\n".join(errors))
            warn("Import failed: " + "; ".join(errors))
            return
        self.translation_key.setText(data["meta"]["translationKey"])
        self.blog_url.setText(data["global"]["blogUrl"])
        self.author.setText(data["global"].get("author", ""))
        policy = data["global"].get("linkPolicy", "no-links")
        policy_map = {
            "no-links": "No links",
            "blog-only": "Blog link only",
            "blog-and-affiliate": "Blog link + optional affiliate link (non-Reddit/Quora only)"
        }
        self.link_policy.setCurrentText(policy_map.get(policy, "No links"))
        locales = data.get("locales", {})
        for locale in ["en", "pt", "es", "it"]:
            loc = locales.get(locale, {})
            self.locale_inputs[locale]["title"].setText(loc.get("title", ""))
            self.locale_inputs[locale]["description"].setText(loc.get("description", ""))
            self.locale_inputs[locale]["content"].setPlainText(loc.get("content", ""))
            self.locale_meta[locale]["tags"] = loc.get("tags", []) or []
            self.locale_meta[locale]["category"] = loc.get("category", "") or ""
            self.locale_meta[locale]["keywords"] = loc.get("keywords", []) or []
            slug = loc.get("slug", "")
            if locale == "en":
                self.post_slug_en.setText(slug)
            if locale == "pt":
                self.post_slug_pt.setText(slug)
            if locale == "es":
                self.post_slug_es.setText(slug)
            if locale == "it":
                self.post_slug_it.setText(slug)
            affiliate = loc.get("affiliate", {})
            if affiliate.get("url"):
                if locale == "en":
                    self.affiliate_en.setText(affiliate.get("url", ""))
                if locale == "pt":
                    self.affiliate_pt.setText(affiliate.get("url", ""))
                if locale == "es":
                    self.affiliate_es.setText(affiliate.get("url", ""))
                if locale == "it":
                    self.affiliate_it.setText(affiliate.get("url", ""))
        info("Content package imported.")
