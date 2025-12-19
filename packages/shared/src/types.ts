export type Locale = 'en' | 'pt' | 'es' | 'it';

export interface GlobalFields {
  translationKey: string;
  author: string;
  affiliateDisclosure: boolean;
  date: string;
  updated?: string;
  editorialIntent: string;
  persona: string;
  trustMode: boolean;
  differentiationHook: string;
}

export interface EnglishArticle {
  title: string;
  description: string;
  slug: string;
  category: string;
  tags: string[];
  content: string;
  faq: string;
}

export interface LocalizedArticle {
  locale: Locale;
  title: string;
  description: string;
  slug: string;
  category: string;
  tags: string[];
  content: string;
  faq?: string[];
}

export interface AffiliateLocaleLinks {
  primary: string;
  secondary?: string[];
  notes?: string;
}

export interface AffiliateLinks {
  en: AffiliateLocaleLinks;
  pt: AffiliateLocaleLinks;
  es: AffiliateLocaleLinks;
  it: AffiliateLocaleLinks;
}

export interface EnglishArticlePackage {
  global: GlobalFields;
  english: EnglishArticle;
  affiliate: {
    en: AffiliateLocaleLinks;
  };
  meta: {
    generatedAt: string;
    version: string;
  };
}

export interface AdminPublishPayload {
  global: GlobalFields;
  localized: Record<Locale, LocalizedArticle>;
  affiliate: AffiliateLinks;
  meta: { generatedAt: string; version: string };
}
