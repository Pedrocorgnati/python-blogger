import { AdminPublishPayload, AffiliateLinks, EnglishArticlePackage, Locale, LocalizedArticle } from '@python-blogger/shared';

export interface TranslatorSettings {
  minWordCount: number;
  minH2Count: number;
  minWordsPerH2: number;
}

export interface InternalSources {
  posts: string[];
  categories: string[];
}

export interface TranslatorState {
  enPackage: EnglishArticlePackage | null;
  affiliateLinks: AffiliateLinks;
  settings: TranslatorSettings;
  internalSources: InternalSources;
}

export interface TranslationParseResult {
  localized: LocalizedArticle;
  translationKey: string;
}

export interface TranslationValidation {
  locale: Locale;
  status: 'pass' | 'warning' | 'fail';
  issues: string[];
}

export interface AdminExportBundle {
  payload: AdminPublishPayload;
  mdxFiles: Record<string, string>;
}
