import {
  AffiliateLinks,
  EnglishArticlePackage,
  LocalizedArticle,
  Locale,
  validators,
  slugify
} from '@python-blogger/shared';
import { InternalSources, TranslationParseResult, TranslationValidation, TranslatorSettings } from './models';

const TRANSLATION_FIELDS = ['title', 'description', 'slug', 'category', 'tags', 'content'] as const;

export const parseTranslationPayload = (locale: Locale, text: string): TranslationParseResult => {
  const trimmed = text.trim();
  const payload: Record<string, string> = {};
  let contentBody = '';

  if (trimmed.startsWith('---')) {
    const endIndex = trimmed.indexOf('---', 3);
    if (endIndex !== -1) {
      const frontmatter = trimmed.slice(3, endIndex).trim();
      frontmatter.split('\n').forEach((line) => {
        const [key, ...rest] = line.split(':');
        if (key && rest.length > 0) {
          payload[key.trim().toLowerCase()] = rest.join(':').trim();
        }
      });
      contentBody = trimmed.slice(endIndex + 3).trim();
    }
  }

  if (!contentBody) {
    const lines = trimmed.split('\n');
    lines.forEach((line) => {
      const match = line.match(/^(TITLE|DESCRIPTION|SLUG|CATEGORY|TAGS):\s*(.*)$/i);
      if (match) {
        payload[match[1].toLowerCase()] = match[2].trim();
      }
    });
    const contentIndex = lines.findIndex((line) => line.toUpperCase().startsWith('CONTENT'));
    if (contentIndex !== -1) {
      contentBody = lines.slice(contentIndex + 1).join('\n').trim();
    }
  }

  const tags = payload.tags
    ? payload.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean)
    : [];

  const localized: LocalizedArticle = {
    locale,
    title: payload.title || '',
    description: payload.description || '',
    slug: payload.slug || '',
    category: payload.category || '',
    tags,
    content: contentBody,
    faq: payload.faq ? payload.faq.split('|').map((item) => item.trim()) : undefined
  };

  return {
    localized,
    translationKey: payload.translationkey || payload.translation_key || ''
  };
};

export const buildLocalizationPrompt = (
  locale: Locale,
  pkg: EnglishArticlePackage,
  affiliate: AffiliateLinks,
  internalSources: InternalSources
) => {
  const targetLinks = affiliate[locale];
  return `You are an expert SEO localization writer. Localize this English blog post for ${
    locale.toUpperCase()
  }.
Do NOT translate literally; adapt for local SEO and natural writing.

RETURN EXACTLY THIS STRUCTURE:
TITLE: ...
DESCRIPTION: ... (max 160 chars)
SLUG: ... (kebab-case)
CATEGORY: ...
TAGS: ... (comma-separated, 6-10)
CONTENT (MDX/Markdown): ...

Global context:
- translationKey: ${pkg.global.translationKey}
- author: ${pkg.global.author}
- editorial intent: ${pkg.global.editorialIntent}
- persona: ${pkg.global.persona}
- trust & accuracy mode: ${pkg.global.trustMode}
- differentiation hook: ${pkg.global.differentiationHook}
- affiliate disclosure enabled: ${pkg.global.affiliateDisclosure}

English source:
TITLE: ${pkg.english.title}
DESCRIPTION: ${pkg.english.description}
SLUG: ${pkg.english.slug}
CATEGORY: ${pkg.english.category}
TAGS: ${pkg.english.tags.join(', ')}
CONTENT:
${pkg.english.content}
FAQ:
${pkg.english.faq}

Internal link sources:
- Existing posts: ${internalSources.posts.join(' | ') || 'none'}
- Existing categories: ${internalSources.categories.join(' | ') || 'none'}

Affiliate links (use at least the primary link 1x, max 3 CTAs):
Primary: ${targetLinks.primary}
Secondary: ${(targetLinks.secondary || []).join(', ') || 'none'}
Notes: ${targetLinks.notes || 'none'}

CTA placement guidance:
- Use placeholders <!-- CTA_1 -->, <!-- CTA_2 -->, <!-- CTA_3 --> from the English content
- Insert CTA blocks near those placeholders

If affiliateDisclosure=true, include a short disclosure at the top of the content.
Output must be copy/paste ready.`;
};

export const validateTranslation = (
  locale: Locale,
  parsed: TranslationParseResult,
  pkg: EnglishArticlePackage,
  affiliate: AffiliateLinks,
  settings: TranslatorSettings
): TranslationValidation => {
  const issues: string[] = [];
  const { localized, translationKey } = parsed;

  TRANSLATION_FIELDS.forEach((field) => {
    if (!(localized as Record<string, string>)[field]) {
      issues.push(`Missing ${field}.`);
    }
  });

  if (translationKey && translationKey !== pkg.global.translationKey) {
    issues.push('translationKey does not match EN package.');
  } else if (!translationKey) {
    issues.push('translationKey missing (add in frontmatter if possible).');
  }

  if (!validators.isKebabCase(localized.slug)) {
    issues.push('Slug is not kebab-case.');
  }

  if (pkg.english.slug && localized.slug === pkg.english.slug) {
    issues.push('Slug matches EN; consider a localized slug.');
  }

  if (localized.tags.length < 6 || localized.tags.length > 10) {
    issues.push('Tags count must be 6-10.');
  }

  const wordCount = localized.content.trim().split(/\s+/).filter(Boolean).length;
  if (wordCount < settings.minWordCount) {
    issues.push(`Content below minimum word count (${settings.minWordCount}).`);
  }

  const h2Count = (localized.content.match(/^##\s+/gm) || []).length;
  if (h2Count < settings.minH2Count) {
    issues.push(`Needs at least ${settings.minH2Count} H2 headings.`);
  }

  const wordsPerH2 = h2Count > 0 ? Math.round(wordCount / h2Count) : 0;
  if (h2Count > 0 && wordsPerH2 < settings.minWordsPerH2) {
    issues.push(`Average words per H2 below ${settings.minWordsPerH2}.`);
  }

  const primaryLink = affiliate[locale].primary;
  if (primaryLink && !localized.content.includes(primaryLink)) {
    issues.push('Primary affiliate link not found in content.');
  }

  if (pkg.global.affiliateDisclosure) {
    const disclosurePattern = /(disclosure|affiliate|afiliad|divulg|publicit)/i;
    if (!disclosurePattern.test(localized.content)) {
      issues.push('Affiliate disclosure not detected.');
    }
  }

  const status = issues.some((issue) => issue.toLowerCase().includes('missing'))
    ? 'fail'
    : issues.length > 0
      ? 'warning'
      : 'pass';

  return { locale, status, issues };
};

export const buildMdxFrontmatter = (
  localized: LocalizedArticle,
  translationKey: string
) => {
  const slug = localized.slug || slugify(localized.title || `${translationKey}-${localized.locale}`);
  return [
    '---',
    `title: ${localized.title}`,
    `description: ${localized.description}`,
    `slug: ${slug}`,
    `category: ${localized.category}`,
    `tags: ${localized.tags.join(', ')}`,
    `translationKey: ${translationKey}`,
    '---'
  ].join('\n');
};
