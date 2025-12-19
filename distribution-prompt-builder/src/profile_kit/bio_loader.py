from __future__ import annotations

import json
import os
from typing import Dict

from .bio_models import BioEntry, BioKit, CHANNELS, LOCALES


def default_bio_entry(locale: str, channel: str) -> BioEntry:
    return BioEntry(
        short_bio=f"{locale.upper()} editor focused on practical tech career guidance.",
        medium_bio=(
            f"{locale.upper()} writer and mentor focused on practical, reputation-first guidance "
            "for early-career technologists."
        ),
        long_bio=(
            f"{locale.upper()} content creator and career mentor. Writes practical, no-hype guidance "
            "on skills, portfolios, and career transitions in tech."
        ),
        one_liner_tagline="Practical tech career guidance, no hype.",
        pinned_post_template="Pinned: My best starter guide for switching into tech.",
        link_policy_notes="Prefer subtle blog link, avoid aggressive CTAs.",
        dos_and_donts="Do: be helpful and transparent. Don't: overpromise or oversell."
    )


def default_bio_kit() -> BioKit:
    profiles: Dict[str, Dict[str, BioEntry]] = {}
    for locale in LOCALES:
        profiles[locale] = {}
        for channel in CHANNELS:
            profiles[locale][channel] = default_bio_entry(locale, channel)
    return BioKit(profiles=profiles)


def load_bio_kit(path: str) -> BioKit:
    if not os.path.exists(path):
        return default_bio_kit()
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return BioKit.from_dict(data)
