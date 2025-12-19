import { EnglishArticlePackage, AdminPublishPayload } from './types';

export const englishArticlePackageSchema = {
  $schema: 'http://json-schema.org/draft-07/schema#',
  title: 'EnglishArticlePackage',
  type: 'object',
  required: ['global', 'english', 'affiliate', 'meta'],
  properties: {
    global: { type: 'object' },
    english: { type: 'object' },
    affiliate: { type: 'object' },
    meta: { type: 'object' }
  }
} as const;

export const adminPublishPayloadSchema = {
  $schema: 'http://json-schema.org/draft-07/schema#',
  title: 'AdminPublishPayload',
  type: 'object',
  required: ['global', 'localized', 'affiliate', 'meta'],
  properties: {
    global: { type: 'object' },
    localized: { type: 'object' },
    affiliate: { type: 'object' },
    meta: { type: 'object' }
  }
} as const;

export const exampleEnglishPackage = (pkg: EnglishArticlePackage) => pkg;
export const exampleAdminPayload = (payload: AdminPublishPayload) => payload;
