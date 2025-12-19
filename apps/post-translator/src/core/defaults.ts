import { AffiliateLinks, EnglishArticlePackage, GlobalFields } from '@python-blogger/shared';
import { InternalSources, TranslatorSettings, TranslatorState } from './models';

export const defaultSettings: TranslatorSettings = {
  minWordCount: 900,
  minH2Count: 3,
  minWordsPerH2: 120
};

export const defaultInternalSources: InternalSources = {
  posts: [],
  categories: []
};

export const emptyAffiliateLinks: AffiliateLinks = {
  en: { primary: '', secondary: [], notes: '' },
  pt: { primary: '', secondary: [], notes: '' },
  es: { primary: '', secondary: [], notes: '' },
  it: { primary: '', secondary: [], notes: '' }
};

export const emptyGlobalFields: GlobalFields = {
  translationKey: '',
  author: '',
  affiliateDisclosure: false,
  date: '',
  updated: '',
  editorialIntent: '',
  persona: '',
  trustMode: false,
  differentiationHook: ''
};

export const createTranslatorState = (): TranslatorState => ({
  enPackage: null,
  affiliateLinks: { ...emptyAffiliateLinks },
  settings: { ...defaultSettings },
  internalSources: { ...defaultInternalSources }
});

export const deriveGlobalFromPackage = (pkg: EnglishArticlePackage): GlobalFields => ({
  translationKey: pkg.global.translationKey,
  author: pkg.global.author || '',
  affiliateDisclosure: pkg.global.affiliateDisclosure || false,
  date: pkg.global.date || '',
  updated: pkg.global.updated || '',
  editorialIntent: pkg.global.editorialIntent || '',
  persona: pkg.global.persona || '',
  trustMode: pkg.global.trustMode || false,
  differentiationHook: pkg.global.differentiationHook || ''
});
