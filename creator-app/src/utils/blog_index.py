from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from utils.logger import warn
from utils.paths import find_repo_root


@dataclass
class BlogTheme:
    title: str
    translation_key: str
    date: str
    category: str
    tags: List[str]
    file_mtime: float


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    lines = parts[1].splitlines()
    data: Dict[str, Any] = {}
    current_list_key: str | None = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- ") and current_list_key:
            data[current_list_key].append(line[2:].strip())
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if value == "":
            data[key] = []
            current_list_key = key
            continue
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
            data[key] = items
            continue
        data[key] = value
    return data


def _parse_date(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return None


def load_latest_blog_themes(limit: int = 20) -> List[BlogTheme]:
    repo_root = find_repo_root()
    if repo_root is None:
        warn("Repo root not found. Cannot load latest blog themes.")
        return []
    posts_dir = repo_root / "content" / "posts" / "en"
    if not posts_dir.exists():
        warn(f"Posts directory not found: {posts_dir}")
        return []

    themes: List[BlogTheme] = []
    for file_path in sorted(posts_dir.glob("*.mdx")):
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            warn(f"Failed to read {file_path}: {exc}")
            continue
        meta = _parse_frontmatter(text)
        title = str(meta.get("title", "")).strip()
        if not title:
            continue
        translation_key = str(meta.get("translationKey", "")).strip()
        date_value = str(meta.get("date", "")).strip()
        category = str(meta.get("category", "")).strip()
        tags = meta.get("tags", []) if isinstance(meta.get("tags", []), list) else []
        themes.append(
            BlogTheme(
                title=title,
                translation_key=translation_key,
                date=date_value,
                category=category,
                tags=tags,
                file_mtime=file_path.stat().st_mtime
            )
        )

    def sort_key(item: BlogTheme) -> datetime:
        parsed = _parse_date(item.date)
        if parsed:
            return parsed
        return datetime.fromtimestamp(item.file_mtime)

    themes.sort(key=sort_key, reverse=True)
    return themes[:limit]
