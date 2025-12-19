from __future__ import annotations

from typing import Dict, List, Tuple

from .channel_rules import CHANNEL_RULES
from .models import AffiliateLinks, GlobalInputs, LocaleContent, PromptResult
from profile_kit.bio_models import BioKit


def _select_bio_text(bio_kit: BioKit, locale: str, channel: str) -> str:
    channel_key = channel
    if channel == "LinkedIn":
        channel_key = "LinkedIn Company Page"
    entry = bio_kit.profiles.get(locale, {}).get(channel_key)
    if not entry:
        return ""
    return entry.medium_bio or entry.short_bio or entry.long_bio or ""


def _build_blog_link(global_inputs: GlobalInputs, locale: str) -> str:
    slug_map = {
        "en": global_inputs.post_slug_en,
        "pt": global_inputs.post_slug_pt or global_inputs.post_slug_en,
        "es": global_inputs.post_slug_es or global_inputs.post_slug_en,
        "it": global_inputs.post_slug_it or global_inputs.post_slug_en
    }
    slug = slug_map.get(locale, global_inputs.post_slug_en)
    return f"{global_inputs.blog_url.rstrip('/')}/{locale}/posts/{slug}"


def _build_affiliate_link(links: AffiliateLinks, locale: str) -> str:
    return getattr(links, locale, "")


def _thumbnail_prompt(theme_hint: str, channel: str) -> str:
    base = (
        "minimal, editorial, modern tech/career aesthetic, abstract shapes or simple symbolic icons, "
        "high readability, clean composition, no clutter, 16:9, no brand logos, "
        "optional 3-6 words max, language matches locale"
    )
    style = "insight card" if channel == "LinkedIn" else "blog cover"
    return (
        f"{base}, style: {style}, theme: {theme_hint}"
    )


def generate_prompts(
    global_inputs: GlobalInputs,
    locale_contents: Dict[str, LocaleContent],
    affiliate_links: AffiliateLinks,
    channels: List[str],
    bio_kit: BioKit
) -> Tuple[Dict[str, str], List[PromptResult]]:
    bundle_by_channel: Dict[str, str] = {}
    flat_results: List[PromptResult] = []
    locales = ["en", "pt", "es", "it"]

    for channel in channels:
        config = CHANNEL_RULES[channel]
        if global_inputs.distribution_mode == "separate":
            bundle_text = _build_bundle_prompt(
                global_inputs=global_inputs,
                locale_contents=locale_contents,
                affiliate_links=affiliate_links,
                channel=channel,
                config=config,
                bio_kit=bio_kit
            )
            if bundle_text:
                bundle_by_channel[channel] = bundle_text
                for locale in locales:
                    content = locale_contents.get(locale)
                    if content and content.content.strip():
                        flat_results.append(
                            PromptResult(channel=channel, locale=locale, variant="A", prompt_text=bundle_text)
                        )
            continue

        variants = ["A", "B"] if global_inputs.generate_variants else ["A"]
        for locale in locales:
            content = locale_contents.get(locale)
            if not content or not content.content.strip():
                continue

            allow_blog, allow_affiliate = _link_rules(global_inputs, channel, config)
            blog_link = _build_blog_link(global_inputs, locale) if allow_blog else ""
            affiliate_link = _build_affiliate_link(affiliate_links, locale) if allow_affiliate else ""

            for variant in variants:
                prompt_text = _build_prompt_text(
                    global_inputs=global_inputs,
                    locale_content=content,
                    channel=channel,
                    config=config,
                    blog_link=blog_link,
                    affiliate_link=affiliate_link,
                    variant=variant,
                    bio_kit=bio_kit
                )
                flat_results.append(
                    PromptResult(channel=channel, locale=locale, variant=variant, prompt_text=prompt_text)
                )

        if flat_results:
            bundle_by_channel[channel] = "\n\n".join(
                [item.prompt_text for item in flat_results if item.channel == channel]
            )

    return bundle_by_channel, flat_results


def _link_rules(global_inputs: GlobalInputs, channel: str, config) -> Tuple[bool, bool]:
    allow_blog = config.allow_blog_link and global_inputs.link_policy != "No links"
    if channel in ("Reddit", "Quora") and global_inputs.link_policy != "No links":
        allow_blog = True
    allow_affiliate = (
        config.allow_affiliate
        and global_inputs.link_policy == "Blog link + optional affiliate link (non-Reddit/Quora only)"
    )

    if channel in ("Reddit", "Quora") and not global_inputs.allow_affiliate_override:
        allow_affiliate = False

    if channel == "LinkedIn" and global_inputs.linkedin_cta_policy == "No links":
        allow_blog = False

    return allow_blog, allow_affiliate


def _build_bundle_prompt(
    global_inputs: GlobalInputs,
    locale_contents: Dict[str, LocaleContent],
    affiliate_links: AffiliateLinks,
    channel: str,
    config,
    bio_kit: BioKit
) -> str:
    locales = ["en", "pt", "es", "it"]
    locale_blocks: List[str] = []
    output_blocks: List[str] = []

    for locale in locales:
        content = locale_contents.get(locale)
        if not content or not content.content.strip():
            continue

        allow_blog, allow_affiliate = _link_rules(global_inputs, channel, config)
        blog_link = _build_blog_link(global_inputs, locale) if allow_blog else ""
        affiliate_link = _build_affiliate_link(affiliate_links, locale) if allow_affiliate else ""

        bio_text = _select_bio_text(bio_kit, locale, channel)
        locale_blocks.append(
            "\n".join(
                [
                    f"=== INPUT LOCALE: {locale.upper()} ===",
                    f"Writer profile (do not repeat verbatim, use as voice reference): {bio_text}",
                    f"Title: {content.title}",
                    f"Description: {content.description}",
                    f"Content: {content.content}",
                    f"Blog link for this locale: {blog_link or 'N/A'}",
                    f"Affiliate link for this locale: {affiliate_link or 'N/A'}"
                ]
            )
        )

        output_blocks.append(
            "\n".join(
                [
                    f"=== LOCALE: {locale.upper()} ===",
                    "POST_TEXT:",
                    "<final post text>",
                    "THUMBNAIL_PROMPT (MIDJOURNEY):",
                    "<N/A or prompt>",
                    "FIRST_COMMENT (LinkedIn only):",
                    "<N/A or comment>",
                    "HASHTAGS (if relevant):",
                    "<LinkedIn 3-8 hashtags, otherwise N/A>",
                    "COMMENTS_TEMPLATES (if enabled):",
                    "<5 short comments or N/A>"
                ]
            )
        )

    if not locale_blocks:
        return ""

    thumb_guidelines = (
        "If thumbnails are allowed, generate a Midjourney prompt: minimal, editorial, modern tech/career aesthetic, "
        "abstract shapes or simple symbolic icons, high readability, clean composition, no clutter, 16:9, "
        "optional 3-6 words max (language matches locale). LinkedIn: insight card. Others: blog cover."
    )

    link_guidance = f"Link policy: {global_inputs.link_policy}."
    if channel == "LinkedIn":
        link_guidance += f" LinkedIn CTA policy: {global_inputs.linkedin_cta_policy}."

    return "\n".join(
        [
            "You are an expert community writer. Generate channel-native content.",
            f"Channel: {channel}",
            "You must produce one output per locale: EN, PT, ES, IT.",
            f"Tone: {global_inputs.tone}",
            f"Persona: {global_inputs.persona}",
            f"Length: {global_inputs.length}",
            f"Main CTA: {global_inputs.main_call_to_action}",
            link_guidance,
            f"Affiliate disclosure: {global_inputs.affiliate_disclosure}",
            "Anti-spam: reputation first, avoid sales language.",
            f"Channel style rules: {config.style_rules}",
            f"LinkedIn first comment enabled: {global_inputs.linkedin_generate_comment}.",
            "If LinkedIn first comment is disabled, return N/A for FIRST_COMMENT.",
            "If thumbnails are not allowed for this channel, return N/A in THUMBNAIL_PROMPT.",
            "If channel is not LinkedIn, FIRST_COMMENT must be N/A.",
            thumb_guidelines,
            "",
            "Inputs:",
            "\n\n".join(locale_blocks),
            "",
            "Return exactly this structure and nothing else:",
            f"CHANNEL: {channel}",
            "\n".join(output_blocks)
        ]
    )


def _build_prompt_text(
    global_inputs: GlobalInputs,
    locale_content: LocaleContent,
    channel: str,
    config,
    blog_link: str,
    affiliate_link: str,
    variant: str,
    bio_kit: BioKit
) -> str:
    length_hint = global_inputs.length
    if config.suggested_length and config.suggested_length.lower() != length_hint:
        length_hint = f"{length_hint} (channel suggests {config.suggested_length})"

    comment_rule = (
        "Include 5 short comment templates in COMMENTS_TEMPLATES."
        if global_inputs.include_comment_templates
        else "Write N/A in COMMENTS_TEMPLATES."
    )

    link_instruction = "No links." if global_inputs.link_policy == "No links" else "Links allowed if relevant."
    if blog_link:
        link_instruction = f"Blog link (discreet): {blog_link}"
    if channel == "LinkedIn" and blog_link:
        link_instruction += f" - {global_inputs.linkedin_cta_policy.lower()}."

    affiliate_instruction = "No affiliate links."
    if affiliate_link:
        affiliate_instruction = f"Affiliate link (use only if contextually helpful): {affiliate_link}"

    thumb_rule = "THUMBNAIL_PROMPT (MIDJOURNEY): N/A"
    if config.allow_thumbnail:
        hint = locale_content.title or locale_content.description or "tech career"
        thumb_rule = f"THUMBNAIL_PROMPT (MIDJOURNEY):\n{_thumbnail_prompt(hint, channel)}"

    channel_style = config.style_rules
    if channel == "Medium":
        channel_style += " Add a note: editorial caution, no overt marketing."

    first_comment_rule = "N/A"
    if channel == "LinkedIn" and global_inputs.linkedin_generate_comment:
        first_comment_rule = "Generate a first comment that adds value, includes a question, and optionally a link per policy."

    output_rules = (
        "Return exactly this structure and nothing else:\n"
        f"CHANNEL: {channel}\n"
        f"=== LOCALE: {locale_content.locale.upper()} ===\n"
        "POST_TEXT:\n"
        "<final post text>\n\n"
        f"{thumb_rule}\n\n"
        "FIRST_COMMENT (LinkedIn only):\n"
        "<comment or N/A>\n\n"
        "HASHTAGS (if relevant):\n"
        "<LinkedIn 3-8 hashtags, otherwise N/A>\n\n"
        "COMMENTS_TEMPLATES (if enabled):\n"
        "<5 short comments or N/A>"
    )

    bio_text = _select_bio_text(bio_kit, locale_content.locale, channel)

    return (
        "You are a channel-native content editor. Produce a final post ready to publish.\n"
        f"Channel: {channel}\n"
        f"Locale: {locale_content.locale}\n"
        f"Writer profile (do not repeat verbatim, use as voice reference): {bio_text}\n"
        f"Tone: {global_inputs.tone}\n"
        f"Persona: {global_inputs.persona}\n"
        f"Length: {length_hint}\n"
        f"Main CTA: {global_inputs.main_call_to_action}\n"
        f"Link policy: {global_inputs.link_policy}. {link_instruction}\n"
        f"Affiliate disclosure: {global_inputs.affiliate_disclosure}\n"
        f"Affiliate rule: {affiliate_instruction}\n"
        f"Anti-spam: reputation first, avoid sales language.\n"
        f"Channel style: {channel_style}\n"
        f"LinkedIn first comment: {first_comment_rule}\n"
        f"Title: {locale_content.title}\n"
        f"Description: {locale_content.description}\n"
        "Content source:\n"
        f"{locale_content.content}\n\n"
        f"{comment_rule}\n\n"
        f"{output_rules}"
    )
