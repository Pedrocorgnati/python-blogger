from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

sample = {
    "meta": {
        "translationKey": "sample-creator-001",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "source": "creator",
        "publishAllLocales": False,
        "localesIncluded": ["en"]
    },
    "global": {
        "author": "Sample Author",
        "blogUrl": "https://example.com",
        "linkPolicy": "blog-only",
        "defaultAffiliateDisclosure": False
    },
    "locales": {
        "en": {
            "title": "How to Start a Tech Career",
            "description": "A practical guide to start a tech career.",
            "slug": "how-to-start-a-tech-career",
            "content": "# How to Start a Tech Career\n\nThis is the EN content...",
            "tags": ["career", "tech"],
            "keywords": ["tech career", "entry level"],
            "category": "Career",
            "affiliate": {"enabled": False, "url": "", "disclosure": ""}
        },
        "pt": {},
        "es": {},
        "it": {}
    }
}

output_path = Path(__file__).resolve().parent / "sample_creator_output.json"
with output_path.open("w", encoding="utf-8") as handle:
    json.dump(sample, handle, indent=2)

print(f"Generated {output_path}")
