from __future__ import annotations

from typing import List, Dict
import os
import re
from urllib.parse import urlparse

from core.models import GlobalInputs, LocaleContent


def validate_inputs(global_inputs: GlobalInputs, locale_contents: List[LocaleContent], channels: List[str]) -> List[str]:
    issues: List[str] = []
    if not global_inputs.translation_key.strip():
        issues.append("Translation key is required.")
    if not global_inputs.blog_url.strip():
        issues.append("Blog URL is required.")
    if not any(item.content.strip() for item in locale_contents if item.locale == "en"):
        issues.append("English content is required.")
    if not channels:
        issues.append("Select at least one channel.")
    return issues


def infer_title_from_content(content: str) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return ""
    if lines[0].startswith("#"):
        return lines[0].lstrip("#").strip()
    return lines[0]


def validate_blog_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def validate_slug(value: str) -> bool:
    if not value:
        return False
    return re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value) is not None


def validate_content_package(payload: Dict[str, object], schema_path: str) -> List[str]:
    errors: List[str] = []
    if not os.path.exists(schema_path):
        errors.append("Schema file not found.")
        return errors
    meta = payload.get("meta", {})
    global_section = payload.get("global", {})
    locales = payload.get("locales", {})

    if not isinstance(meta, dict):
        errors.append("meta must be an object.")
    if not isinstance(global_section, dict):
        errors.append("global must be an object.")
    if not isinstance(locales, dict):
        errors.append("locales must be an object.")

    if not meta.get("translationKey"):
        errors.append("meta.translationKey is required.")
    if not meta.get("createdAt"):
        errors.append("meta.createdAt is required.")
    if meta.get("source") not in ("creator", "translator", "manual"):
        errors.append("meta.source must be creator|translator|manual.")

    if not global_section.get("blogUrl"):
        errors.append("global.blogUrl is required.")
    if global_section.get("linkPolicy") not in ("no-links", "blog-only", "blog-and-affiliate"):
        errors.append("global.linkPolicy must be no-links|blog-only|blog-and-affiliate.")

    for locale in ["en", "pt", "es", "it"]:
        locale_entry = locales.get(locale, {})
        if not isinstance(locale_entry, dict):
            errors.append(f"locales.{locale} must be an object.")
            continue
        title = locale_entry.get("title", "")
        slug = locale_entry.get("slug", "")
        content = locale_entry.get("content", "")
        if title and not isinstance(title, str):
            errors.append(f"locales.{locale}.title must be string.")
        if slug and not isinstance(slug, str):
            errors.append(f"locales.{locale}.slug must be string.")
        if content and not isinstance(content, str):
            errors.append(f"locales.{locale}.content must be string.")
        if locale == "en":
            if not locale_entry.get("title"):
                errors.append("locales.en.title is required.")
            if not locale_entry.get("slug"):
                errors.append("locales.en.slug is required.")
            if not locale_entry.get("content"):
                errors.append("locales.en.content is required.")

    return errors
