from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CreatorInputs:
    theme: str
    translation_key: str
    author: str
    blog_url: str
    title: str
    description: str
    slug: str
    tags: List[str]
    category: str
    keywords: List[str]
    affiliate_enabled: bool
    affiliate_url: str
    affiliate_disclosure: str
    content: str
    link_policy: str
    default_affiliate_disclosure: bool
