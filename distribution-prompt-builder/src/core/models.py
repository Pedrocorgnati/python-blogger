from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GlobalInputs:
    translation_key: str
    author: str
    affiliate_disclosure: bool
    blog_url: str
    post_slug_en: str
    post_slug_pt: str
    post_slug_es: str
    post_slug_it: str
    main_call_to_action: str
    link_policy: str
    tone: str
    persona: str
    length: str
    generate_variants: bool
    include_comment_templates: bool
    allow_affiliate_override: bool
    distribution_mode: str
    linkedin_generate_comment: bool
    linkedin_cta_policy: str


@dataclass
class LocaleContent:
    locale: str
    title: str
    description: str
    content: str


@dataclass
class AffiliateLinks:
    en: str
    pt: str
    es: str
    it: str


@dataclass
class ChannelConfig:
    name: str
    allow_thumbnail: bool
    allow_affiliate: bool
    allow_blog_link: bool
    suggested_length: str
    style_rules: str


@dataclass
class PromptResult:
    channel: str
    locale: str
    variant: str
    prompt_text: str
