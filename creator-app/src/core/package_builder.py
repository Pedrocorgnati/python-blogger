from __future__ import annotations

from datetime import datetime
from typing import Dict

from core.models import CreatorInputs


def build_content_package(inputs: CreatorInputs) -> Dict[str, object]:
    now = datetime.utcnow().isoformat()
    return {
        "meta": {
            "translationKey": inputs.translation_key,
            "createdAt": now,
            "updatedAt": now,
            "source": "creator",
            "publishAllLocales": False,
            "localesIncluded": ["en"]
        },
        "global": {
            "author": inputs.author,
            "blogUrl": inputs.blog_url,
            "linkPolicy": inputs.link_policy,
            "defaultAffiliateDisclosure": inputs.default_affiliate_disclosure,
            "theme": inputs.theme
        },
        "locales": {
            "en": {
                "title": inputs.title,
                "description": inputs.description,
                "slug": inputs.slug,
                "content": inputs.content,
                "keywords": inputs.keywords,
                "tags": inputs.tags,
                "category": inputs.category,
                "affiliate": {
                    "enabled": inputs.affiliate_enabled,
                    "url": inputs.affiliate_url,
                    "disclosure": inputs.affiliate_disclosure
                }
            },
            "pt": {},
            "es": {},
            "it": {}
        }
    }
