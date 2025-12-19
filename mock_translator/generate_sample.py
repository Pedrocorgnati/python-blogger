from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

sample = {
    "meta": {
        "translationKey": "sample-translator-001",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "source": "translator",
        "publishAllLocales": True,
        "localesIncluded": ["en", "pt", "es", "it"]
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
        "pt": {
            "title": "Como iniciar uma carreira em tecnologia",
            "description": "Guia pratico para iniciar na tecnologia.",
            "slug": "como-iniciar-carreira-tecnologia",
            "content": "# Como iniciar uma carreira em tecnologia\n\nConteudo PT...",
            "tags": ["carreira", "tecnologia"],
            "keywords": ["carreira tech"],
            "category": "Carreira",
            "affiliate": {"enabled": False, "url": "", "disclosure": ""}
        },
        "es": {
            "title": "Como empezar una carrera en tecnologia",
            "description": "Guia practico para empezar en tecnologia.",
            "slug": "como-empezar-carrera-tecnologia",
            "content": "# Como empezar una carrera en tecnologia\n\nContenido ES...",
            "tags": ["carrera", "tecnologia"],
            "keywords": ["carrera tech"],
            "category": "Carrera",
            "affiliate": {"enabled": False, "url": "", "disclosure": ""}
        },
        "it": {
            "title": "Come iniziare una carriera tech",
            "description": "Guida pratica per iniziare in tech.",
            "slug": "come-iniziare-carriera-tech",
            "content": "# Come iniziare una carriera tech\n\nContenuto IT...",
            "tags": ["carriera", "tech"],
            "keywords": ["carriera tech"],
            "category": "Carriera",
            "affiliate": {"enabled": False, "url": "", "disclosure": ""}
        }
    }
}

output_path = Path(__file__).resolve().parent / "sample_translator_output.json"
with output_path.open("w", encoding="utf-8") as handle:
    json.dump(sample, handle, indent=2)

print(f"Generated {output_path}")
