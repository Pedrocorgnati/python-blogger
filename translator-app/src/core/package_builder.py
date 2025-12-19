from __future__ import annotations

from datetime import datetime
from typing import Dict, List


def build_translator_package(
    base: Dict[str, object],
    locales: Dict[str, Dict[str, object]],
    publish_all: bool,
    locales_included: List[str]
) -> Dict[str, object]:
    now = datetime.utcnow().isoformat()
    meta = base.get("meta", {})
    meta.update({
        "updatedAt": now,
        "source": "translator",
        "publishAllLocales": publish_all,
        "localesIncluded": locales_included
    })

    payload = {
        "meta": meta,
        "global": base.get("global", {}),
        "locales": locales
    }
    return payload


def build_blog_admin_package(translation_key: str, locales: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    return {
        "translationKey": translation_key,
        "columns": {
            locale: {
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "slug": data.get("slug", ""),
                "content": data.get("content", ""),
                "tags": data.get("tags", []),
                "category": data.get("category", ""),
                "keywords": data.get("keywords", []),
                "affiliate": data.get("affiliate", {})
            }
            for locale, data in locales.items()
        }
    }
