import React, { useEffect, useMemo, useState } from 'react';
import { open } from '@tauri-apps/api/dialog';
import { readTextFile } from '@tauri-apps/api/fs';
import { writeText } from '@tauri-apps/api/clipboard';
import {
  AdminPublishPayload,
  EnglishArticlePackage,
  Locale,
  LocalizedArticle
} from '@python-blogger/shared';
import Sidebar, { PageKey } from './components/Sidebar';
import ImportPage from './pages/ImportPage';
import AffiliatePage from './pages/AffiliatePage';
import PromptsPage from './pages/PromptsPage';
import ValidationPage from './pages/ValidationPage';
import TranslationCheckPage from './pages/TranslationCheckPage';
import ExportPage from './pages/ExportPage';
import SettingsPage from './pages/SettingsPage';
import {
  createTranslatorState,
  deriveGlobalFromPackage,
  emptyGlobalFields
} from './core/defaults';
import { TranslationValidation } from './core/models';
import {
  buildLocalizationPrompt,
  buildMdxFrontmatter,
  parseTranslationPayload,
  validateTranslation
} from './core/utils';
import { exportMdxFiles, getAppDataPath, openExportsFolder, saveExportJson, savePrompt } from './core/storage';
import { validateEnglishPackage } from '@python-blogger/shared';

const APP_VERSION = '0.1.0';

const defaultPromptState: Record<Locale, string> = {
  en: '',
  pt: '',
  es: '',
  it: ''
};

const App: React.FC = () => {
  const [page, setPage] = useState<PageKey>('import');
  const [state, setState] = useState(createTranslatorState());
  const [globalFields, setGlobalFields] = useState(emptyGlobalFields);
  const [prompts, setPrompts] = useState<Record<Locale, string>>(defaultPromptState);
  const [message, setMessage] = useState<string>('');
  const [translationInputs, setTranslationInputs] = useState<Record<Locale, string>>({
    en: '',
    pt: '',
    es: '',
    it: ''
  });

  useEffect(() => {
    const init = async () => {
      const appPath = await getAppDataPath();
      setMessage(`App data: ${appPath}`);
    };
    init();
  }, []);

  const showMessage = (text: string) => {
    setMessage(text);
    setTimeout(() => setMessage(''), 4000);
  };

  const handleImportPackage = (pkg: EnglishArticlePackage) => {
    const issues = validateEnglishPackage(pkg);
    if (issues.length > 0) {
      showMessage(`Import warnings: ${issues.join(' ')}`);
    } else {
      showMessage('EN package imported.');
    }

    setState((prev) => ({
      ...prev,
      enPackage: pkg,
      affiliateLinks: {
        ...prev.affiliateLinks,
        en: pkg.affiliate.en || prev.affiliateLinks.en
      }
    }));
    setGlobalFields(deriveGlobalFromPackage(pkg));
  };

  const handleImportJson = (value: string) => {
    try {
      const parsed = JSON.parse(value) as EnglishArticlePackage;
      handleImportPackage(parsed);
    } catch {
      showMessage('Invalid JSON.');
    }
  };

  const handleOpenFile = async () => {
    const selected = await open({
      filters: [{ name: 'JSON', extensions: ['json'] }]
    });
    if (!selected || Array.isArray(selected)) return;
    const contents = await readTextFile(selected);
    handleImportJson(contents);
  };

  const translationReports: TranslationValidation[] = useMemo(() => {
    if (!state.enPackage) return [];
    return (['pt', 'es', 'it'] as Locale[]).map((locale) =>
      validateTranslation(
        locale,
        parseTranslationPayload(locale, translationInputs[locale]),
        state.enPackage,
        state.affiliateLinks,
        state.settings
      )
    );
  }, [state.enPackage, state.affiliateLinks, state.settings, translationInputs]);

  const hasBlockingIssues = useMemo(() => {
    if (!state.enPackage) return true;
    return translationReports.some((report) => report.status === 'fail');
  }, [state.enPackage, translationReports]);

  const handleGeneratePrompts = (locale?: Locale) => {
    if (!state.enPackage) {
      showMessage('Import EN package first.');
      return;
    }
    const generateFor = (target: Locale) => {
      const prompt = buildLocalizationPrompt(
        target,
        { ...state.enPackage, global: globalFields },
        state.affiliateLinks,
        state.internalSources
      );
      setPrompts((prev) => ({ ...prev, [target]: prompt }));
    };

    if (locale) {
      generateFor(locale);
      showMessage(`Prompt generated for ${locale.toUpperCase()}.`);
      return;
    }

    (['pt', 'es', 'it'] as Locale[]).forEach((target) => generateFor(target));
    showMessage('All prompts generated.');
  };

  const handleCopy = async (text: string) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      await writeText(text);
    }
    showMessage('Copied to clipboard.');
  };

  const handleSavePrompt = async (locale: Locale) => {
    if (!state.enPackage) return;
    const prompt = prompts[locale];
    if (!prompt) {
      showMessage('Generate the prompt first.');
      return;
    }
    await savePrompt(globalFields.translationKey || 'draft', locale, prompt);
    showMessage(`Prompt saved for ${locale.toUpperCase()}.`);
  };

  const buildPayload = (): AdminPublishPayload | null => {
    if (!state.enPackage) return null;

    const localized: Record<Locale, LocalizedArticle> = {
      en: {
        locale: 'en',
        title: state.enPackage.english.title,
        description: state.enPackage.english.description,
        slug: state.enPackage.english.slug,
        category: state.enPackage.english.category,
        tags: state.enPackage.english.tags,
        content: state.enPackage.english.content,
        faq: state.enPackage.english.faq ? [state.enPackage.english.faq] : undefined
      },
      pt: parseTranslationPayload('pt', translationInputs.pt).localized,
      es: parseTranslationPayload('es', translationInputs.es).localized,
      it: parseTranslationPayload('it', translationInputs.it).localized
    };

    return {
      global: globalFields,
      localized,
      affiliate: state.affiliateLinks,
      meta: { generatedAt: new Date().toISOString(), version: APP_VERSION }
    };
  };

  const payload = useMemo(() => buildPayload(), [state.enPackage, translationInputs, globalFields, state.affiliateLinks]);
  const payloadJson = useMemo(() => (payload ? JSON.stringify(payload, null, 2) : ''), [payload]);

  const handleExportJson = async () => {
    if (!payload) {
      showMessage('Import EN package first.');
      return;
    }
    if (hasBlockingIssues) {
      showMessage('Resolve validation failures before exporting.');
      return;
    }
    await saveExportJson(globalFields.translationKey || 'draft', payloadJson);
    showMessage('Payload JSON exported.');
  };

  const handleExportMdx = async () => {
    if (!payload) {
      showMessage('Import EN package first.');
      return;
    }
    if (hasBlockingIssues) {
      showMessage('Resolve validation failures before exporting.');
      return;
    }

    const mdxPayload: Record<string, string> = {};
    (['en', 'pt', 'es', 'it'] as Locale[]).forEach((locale) => {
      const localized = payload.localized[locale];
      const frontmatter = buildMdxFrontmatter(localized, globalFields.translationKey);
      const content = `${frontmatter}\n\n${localized.content || '<!-- content here -->'}`;
      mdxPayload[`mdx/${locale}/${localized.slug || locale}.mdx`] = content;
    });

    await exportMdxFiles(mdxPayload);
    showMessage('MDX skeletons exported.');
  };

  const renderPage = () => {
    switch (page) {
      case 'import':
        return (
          <ImportPage enPackage={state.enPackage} onImportJson={handleImportJson} onOpenFile={handleOpenFile} />
        );
      case 'affiliate':
        return (
          <AffiliatePage
            affiliate={state.affiliateLinks}
            onUpdate={(affiliateLinks) => setState((prev) => ({ ...prev, affiliateLinks }))}
          />
        );
      case 'prompts':
        return (
          <PromptsPage
            prompts={prompts}
            blocked={!state.enPackage}
            onGenerate={handleGeneratePrompts}
            onCopy={(locale) => handleCopy(prompts[locale])}
            onSave={handleSavePrompt}
          />
        );
      case 'validation':
        return (
          <ValidationPage
            reports={translationReports}
            minWordCount={state.settings.minWordCount}
            minH2Count={state.settings.minH2Count}
            minWordsPerH2={state.settings.minWordsPerH2}
          />
        );
      case 'translation':
        return (
          <TranslationCheckPage
            values={translationInputs}
            reports={translationReports}
            onChange={(locale, value) =>
              setTranslationInputs((prev) => ({ ...prev, [locale]: value }))
            }
          />
        );
      case 'export':
        return (
          <ExportPage
            payloadJson={payloadJson}
            blocked={hasBlockingIssues}
            onCopy={() => handleCopy(payloadJson)}
            onSave={handleExportJson}
            onExportMdx={handleExportMdx}
            onOpenExports={openExportsFolder}
          />
        );
      case 'settings':
        return (
          <SettingsPage
            global={globalFields}
            settings={state.settings}
            internalSources={state.internalSources}
            onUpdateGlobal={setGlobalFields}
            onUpdateSettings={(settings) => setState((prev) => ({ ...prev, settings }))}
            onUpdateSources={(internalSources) => setState((prev) => ({ ...prev, internalSources }))}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden text-white">
      <Sidebar current={page} onNavigate={setPage} />
      <main className="flex-1 overflow-y-auto p-8">
        {message && (
          <div className="mb-6 rounded-full bg-white/10 px-4 py-2 text-xs text-white/70">
            {message}
          </div>
        )}
        {renderPage()}
      </main>
    </div>
  );
};

export default App;
