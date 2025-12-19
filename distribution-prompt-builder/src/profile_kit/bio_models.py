from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

CHANNELS = ["Reddit", "Quora", "Dev.to", "Hashnode", "Medium", "LinkedIn Company Page"]
LOCALES = ["en", "pt", "es", "it"]
BIO_FIELDS = [
    "short_bio",
    "medium_bio",
    "long_bio",
    "one_liner_tagline",
    "pinned_post_template",
    "link_policy_notes",
    "dos_and_donts"
]


@dataclass
class BioEntry:
    short_bio: str = ""
    medium_bio: str = ""
    long_bio: str = ""
    one_liner_tagline: str = ""
    pinned_post_template: str = ""
    link_policy_notes: str = ""
    dos_and_donts: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "short_bio": self.short_bio,
            "medium_bio": self.medium_bio,
            "long_bio": self.long_bio,
            "one_liner_tagline": self.one_liner_tagline,
            "pinned_post_template": self.pinned_post_template,
            "link_policy_notes": self.link_policy_notes,
            "dos_and_donts": self.dos_and_donts
        }

    @staticmethod
    def from_dict(data: Dict[str, str]) -> "BioEntry":
        return BioEntry(
            short_bio=data.get("short_bio", ""),
            medium_bio=data.get("medium_bio", ""),
            long_bio=data.get("long_bio", ""),
            one_liner_tagline=data.get("one_liner_tagline", ""),
            pinned_post_template=data.get("pinned_post_template", ""),
            link_policy_notes=data.get("link_policy_notes", ""),
            dos_and_donts=data.get("dos_and_donts", "")
        )


@dataclass
class BioKit:
    profiles: Dict[str, Dict[str, BioEntry]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        return {
            locale: {channel: entry.to_dict() for channel, entry in channels.items()}
            for locale, channels in self.profiles.items()
        }

    @staticmethod
    def from_dict(data: Dict[str, Dict[str, Dict[str, str]]]) -> "BioKit":
        profiles: Dict[str, Dict[str, BioEntry]] = {}
        for locale, channels in data.items():
            profiles[locale] = {
                channel: BioEntry.from_dict(entry)
                for channel, entry in channels.items()
            }
        return BioKit(profiles=profiles)
