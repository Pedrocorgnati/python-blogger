from __future__ import annotations

from typing import Dict

from .models import ChannelConfig


CHANNEL_RULES: Dict[str, ChannelConfig] = {
    "Reddit": ChannelConfig(
        name="Reddit",
        allow_thumbnail=False,
        allow_affiliate=False,
        allow_blog_link=False,
        suggested_length="short",
        style_rules="Value-first, community-friendly, no marketing, no heavy CTA. Encourage discussion."
    ),
    "Quora": ChannelConfig(
        name="Quora",
        allow_thumbnail=False,
        allow_affiliate=False,
        allow_blog_link=False,
        suggested_length="standard",
        style_rules="Q&A format with a suggested question, authoritative and practical steps."
    ),
    "Dev.to": ChannelConfig(
        name="Dev.to",
        allow_thumbnail=True,
        allow_affiliate=True,
        allow_blog_link=True,
        suggested_length="standard",
        style_rules="Technical editorial, helpful, structured headings, adapted-from footer with blog link."
    ),
    "Hashnode": ChannelConfig(
        name="Hashnode",
        allow_thumbnail=True,
        allow_affiliate=True,
        allow_blog_link=True,
        suggested_length="standard",
        style_rules="Similar to Dev.to, short structured sections, adapted-from footer with blog link."
    ),
    "LinkedIn": ChannelConfig(
        name="LinkedIn",
        allow_thumbnail=True,
        allow_affiliate=False,
        allow_blog_link=True,
        suggested_length="long",
        style_rules="Hook + skimmable structure + credibility. Must generate first comment."
    ),
    "Medium": ChannelConfig(
        name="Medium",
        allow_thumbnail=True,
        allow_affiliate=True,
        allow_blog_link=True,
        suggested_length="long",
        style_rules="Editorial tone, no marketing, blog link discreet at end."
    )
}
