import { EnglishArticle, EnglishArticlePackage, GlobalFields, slugify } from '@python-blogger/shared';

export interface PromptInputs {
  theme: string;
  affiliateLink: string;
  extraBrief: string;
  editorialIntent: string;
  persona: string;
  trustMode: boolean;
  differentiationHook: string;
  articleType: string;
  length: string;
}

export const buildPerplexityPrompt = (inputs: PromptInputs) => {
  return `You are an expert SEO writer. Create a high-quality English blog article.

Topic/theme: ${inputs.theme}
Affiliate link to include (at least 1 CTA): ${inputs.affiliateLink}
Editorial intent: ${inputs.editorialIntent}
Writer persona: ${inputs.persona}
Trust & accuracy mode: ${inputs.trustMode}
Differentiation hook: ${inputs.differentiationHook || 'none'}
Article type: ${inputs.articleType}
Length target: ${inputs.length}
Extra brief: ${inputs.extraBrief || 'none'}

Include CTA placeholders in the content:
<!-- CTA_1 --> after intro
<!-- CTA_2 --> after a high-intent section
<!-- CTA_3 --> before FAQ or conclusion

RETURN EXACTLY THIS STRUCTURE:
TITLE:
DESCRIPTION:
SLUG:
CATEGORY:
TAGS:
CONTENT (MDX/Markdown):
FAQ:

Notes:
- Keep DESCRIPTION <= 160 characters.
- TAGS should be comma-separated (6-10).
- Use professional, direct writing and solid headings.`;
};

export const parsePerplexityOutput = (text: string): EnglishArticle => {
  const payload: Record<string, string> = {};
  const lines = text.trim().split('\n');
  lines.forEach((line) => {
    const match = line.match(/^(TITLE|DESCRIPTION|SLUG|CATEGORY|TAGS|FAQ):\s*(.*)$/i);
    if (match) {
      payload[match[1].toLowerCase()] = match[2].trim();
    }
  });

  const contentIndex = lines.findIndex((line) => line.toUpperCase().startsWith('CONTENT'));
  const content = contentIndex !== -1 ? lines.slice(contentIndex + 1).join('\n').trim() : '';

  return {
    title: payload.title || '',
    description: payload.description || '',
    slug: payload.slug || '',
    category: payload.category || '',
    tags: payload.tags ? payload.tags.split(',').map((tag) => tag.trim()).filter(Boolean) : [],
    content,
    faq: payload.faq || ''
  };
};

export const generateTranslationKey = (title: string) => {
  const slug = slugify(title || 'article');
  const date = new Date();
  const stamp = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(
    date.getDate()
  ).padStart(2, '0')}`;
  return `${slug}-${stamp}`;
};

export const buildEnglishPackage = (
  global: GlobalFields,
  english: EnglishArticle,
  affiliateLink: string,
  version: string
): EnglishArticlePackage => ({
  global,
  english,
  affiliate: {
    en: {
      primary: affiliateLink,
      secondary: [],
      notes: ''
    }
  },
  meta: {
    generatedAt: new Date().toISOString(),
    version
  }
});
