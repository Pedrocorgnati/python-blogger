from __future__ import annotations

from typing import Dict, List

from .bio_models import CHANNELS, LOCALES


def build_bio_generation_prompt(locale: str) -> str:
    channels = ", ".join(CHANNELS)
    return (
        "You are an editorial brand strategist. Create a Profile & Bio Kit.\n"
        f"Locale: {locale.upper()}\n"
        f"Channels: {channels}\n\n"
        "Rules:\n"
        "- Reputation first, no aggressive marketing.\n"
        "- No financial promises.\n"
        "- Human, editorial, trustworthy tone.\n"
        "- Adapt culturally for the locale.\n\n"
        "Return JSON with this structure:\n"
        "{\n"
        "  \"Reddit\": {\"short_bio\":\"\", \"medium_bio\":\"\", \"long_bio\":\"\", \"one_liner_tagline\":\"\", \"pinned_post_template\":\"\", \"link_policy_notes\":\"\", \"dos_and_donts\":\"\"},\n"
        "  \"Quora\": {...},\n"
        "  \"Dev.to\": {...},\n"
        "  \"Hashnode\": {...},\n"
        "  \"Medium\": {...},\n"
        "  \"LinkedIn Company Page\": {\"short_bio\":\"\", \"medium_bio\":\"\", \"long_bio\":\"\", \"one_liner_tagline\":\"\", \"pinned_post_template\":\"\", \"link_policy_notes\":\"\", \"dos_and_donts\":\"\"}\n"
        "}\n"
        "For LinkedIn Company Page, include: tagline, about (short+long), specialties, first post template, 5 post ideas in the fields provided."
    )


def build_bio_generation_prompt_all() -> str:
    prompts = [build_bio_generation_prompt(locale) for locale in LOCALES]
    return "\n\n---\n\n".join(prompts)
