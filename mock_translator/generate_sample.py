from __future__ import annotations

import json
from datetime import datetime

sample = {
    "meta": {
        "translationKey": "sample-translator-001",
        "createdAt": datetime.utcnow().isoformat(),
        "source": "translator"
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
        "pt": {
            "title": "Como iniciar uma carreira em tecnologia",
            "slug": "como-iniciar-carreira-tecnologia",
            "content": "# Como iniciar uma carreira em tecnologia\n\nConteudo PT..."
        },
        "es": {
            "title": "Como empezar una carrera en tecnologia",
            "slug": "como-empezar-carrera-tecnologia",
            "content": "# Como empezar una carrera en tecnologia\n\nContenido ES..."
        },
        "it": {
            "title": "Come iniziare una carriera tech",
            "slug": "come-iniziare-carriera-tech",
            "content": "# Come iniziare una carriera tech\n\nContenuto IT..."
        }
    }
}

with open("sample_translator_output.json", "w", encoding="utf-8") as handle:
    json.dump(sample, handle, indent=2)

print("Generated sample_translator_output.json")
