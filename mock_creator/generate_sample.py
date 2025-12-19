from __future__ import annotations

import json
from datetime import datetime

sample = {
    "meta": {
        "translationKey": "sample-creator-001",
        "createdAt": datetime.utcnow().isoformat(),
        "source": "creator"
    },
    "global": {
        "author": "Sample Author",
        "blogUrl": "https://example.com",
        "linkPolicy": "blog-only"
    },
    "locales": {
        "en": {
            "title": "How to Start a Tech Career",
            "slug": "how-to-start-a-tech-career",
            "content": "# How to Start a Tech Career\n\nThis is the EN content..."
        },
        "pt": {},
        "es": {},
        "it": {}
    }
}

with open("sample_creator_output.json", "w", encoding="utf-8") as handle:
    json.dump(sample, handle, indent=2)

print("Generated sample_creator_output.json")
