import { EnglishArticlePackage, GlobalFields, Locale } from './types';

export const stripDiacritics = (value: string) =>
  value.normalize('NFD').replace(/[\u0300-\u036f]/g, '');

export const kebabCase = (value: string) =>
  value
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');

export const slugify = (value: string, maxLength = 60) => {
  const stripped = stripDiacritics(value).toLowerCase();
  const clean = stripped.replace(/[^a-z0-9\s-]/g, ' ').replace(/\s+/g, ' ');
  return kebabCase(clean).slice(0, maxLength);
};

export const validators = {
  isKebabCase: (value: string) => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value),
  hasMinWords: (value: string, min: number) => value.trim().split(/\s+/).filter(Boolean).length >= min,
  hasMinH2: (value: string, min: number) => (value.match(/^##\s+/gm) || []).length >= min
};

export const validateEnglishPackage = (pkg: EnglishArticlePackage) => {
  const issues: string[] = [];
  if (!pkg.global.translationKey) issues.push('translationKey missing.');
  if (!pkg.english.title) issues.push('English title missing.');
  if (!pkg.english.description) issues.push('English description missing.');
  if (!validators.isKebabCase(pkg.english.slug)) issues.push('English slug not kebab-case.');
  if (pkg.english.tags.length < 4) issues.push('English tags too few.');
  if (!pkg.english.content) issues.push('English content missing.');
  return issues;
};

export const localeLabel = (locale: Locale) => locale.toUpperCase();
