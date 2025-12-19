import React, { useEffect, useMemo, useState } from 'react';
import { writeText } from '@tauri-apps/api/clipboard';
import { EnglishArticle, GlobalFields, validators, slugify } from '@python-blogger/shared';
import { buildEnglishPackage, buildPerplexityPrompt, generateTranslationKey, parsePerplexityOutput, PromptInputs } from './core/utils';
import { getAppDataPath, openExportsFolder, saveEnglishPackage } from './core/storage';

const APP_VERSION = '0.1.0';

const defaultArticle: EnglishArticle = {
  title: '',
  description: '',
  slug: '',
  category: '',
  tags: [],
  content: '',
  faq: ''
};

const App: React.FC = () => {
  const [inputs, setInputs] = useState<PromptInputs>({
    theme: '',
    affiliateLink: '',
    extraBrief: '',
    editorialIntent: 'educate',
    persona: 'career coach',
    trustMode: true,
    differentiationHook: '',
    articleType: 'how-to',
    length: 'standard'
  });
  const [perplexityOutput, setPerplexityOutput] = useState('');
  const [article, setArticle] = useState<EnglishArticle>(defaultArticle);
  const [translationKey, setTranslationKey] = useState('');
  const [message, setMessage] = useState('');

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

  const prompt = useMemo(() => buildPerplexityPrompt(inputs), [inputs]);

  const globalFields: GlobalFields = useMemo(
    () => ({
      translationKey,
      author: '',
      affiliateDisclosure: false,
      date: '',
      updated: '',
      editorialIntent: inputs.editorialIntent,
      persona: inputs.persona,
      trustMode: inputs.trustMode,
      differentiationHook: inputs.differentiationHook
    }),
    [inputs, translationKey]
  );

  const englishPackage = useMemo(() => {
    return buildEnglishPackage(globalFields, article, inputs.affiliateLink, APP_VERSION);
  }, [globalFields, article, inputs.affiliateLink]);

  const payloadJson = useMemo(() => JSON.stringify(englishPackage, null, 2), [englishPackage]);

  const handleCopy = async (text: string) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      await writeText(text);
    }
    showMessage('Copied to clipboard.');
  };

  const handleParseOutput = () => {
    const parsed = parsePerplexityOutput(perplexityOutput);
    const slug = parsed.slug && validators.isKebabCase(parsed.slug) ? parsed.slug : slugify(parsed.title);
    setArticle({ ...parsed, slug });
    setTranslationKey(generateTranslationKey(parsed.title));
    showMessage('Perplexity output parsed.');
  };

  const handleSavePackage = async () => {
    if (!translationKey) {
      showMessage('Generate a translation key first.');
      return;
    }
    await saveEnglishPackage(translationKey, payloadJson);
    showMessage('EN Article Package exported.');
  };

  return (
    <div className="min-h-screen px-8 py-10 text-white">
      {message && (
        <div className="mb-6 rounded-full bg-white/10 px-4 py-2 text-xs text-white/70">
          {message}
        </div>
      )}

      <div className="flex flex-col gap-6">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-white/50">post-creator</div>
          <h1 className="text-3xl font-semibold text-white">Perplexity Prompt Builder</h1>
          <p className="subtle">Craft the English prompt, then package the final EN article for translation.</p>
        </div>

        <section className="card p-6">
          <h2 className="section-title">Prompt inputs</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="subtle">Theme / Topic</span>
              <input
                className="input"
                value={inputs.theme}
                onChange={(event) => setInputs({ ...inputs, theme: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Affiliate link</span>
              <input
                className="input"
                value={inputs.affiliateLink}
                onChange={(event) => setInputs({ ...inputs, affiliateLink: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Editorial intent</span>
              <select
                className="input"
                value={inputs.editorialIntent}
                onChange={(event) => setInputs({ ...inputs, editorialIntent: event.target.value })}
              >
                <option value="educate">educate</option>
                <option value="decide">decide</option>
                <option value="convert">convert</option>
                <option value="validate">validate</option>
              </select>
            </label>
            <label className="space-y-2">
              <span className="subtle">Writer persona</span>
              <input
                className="input"
                value={inputs.persona}
                onChange={(event) => setInputs({ ...inputs, persona: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Article type</span>
              <select
                className="input"
                value={inputs.articleType}
                onChange={(event) => setInputs({ ...inputs, articleType: event.target.value })}
              >
                <option value="roadmap">roadmap</option>
                <option value="comparison">comparison</option>
                <option value="how-to">how-to</option>
                <option value="certifications">certifications</option>
                <option value="best-courses">best courses</option>
              </select>
            </label>
            <label className="space-y-2">
              <span className="subtle">Length</span>
              <select
                className="input"
                value={inputs.length}
                onChange={(event) => setInputs({ ...inputs, length: event.target.value })}
              >
                <option value="short">short</option>
                <option value="standard">standard</option>
                <option value="long">long</option>
              </select>
            </label>
            <label className="space-y-2">
              <span className="subtle">Differentiation hook</span>
              <input
                className="input"
                value={inputs.differentiationHook}
                onChange={(event) => setInputs({ ...inputs, differentiationHook: event.target.value })}
              />
            </label>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={inputs.trustMode}
                onChange={(event) => setInputs({ ...inputs, trustMode: event.target.checked })}
              />
              <span className="subtle">Trust & accuracy mode</span>
            </label>
          </div>
          <label className="mt-4 block space-y-2">
            <span className="subtle">Extra brief</span>
            <textarea
              className="textarea min-h-[120px]"
              value={inputs.extraBrief}
              onChange={(event) => setInputs({ ...inputs, extraBrief: event.target.value })}
            />
          </label>
        </section>

        <section className="card p-6">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Perplexity prompt</h2>
            <button className="btn btn-outline" onClick={() => handleCopy(prompt)}>
              Copy prompt
            </button>
          </div>
          <textarea className="textarea mt-4 min-h-[260px] font-mono text-xs" value={prompt} readOnly />
        </section>

        <section className="card p-6">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Perplexity output</h2>
            <button className="btn btn-ghost" onClick={handleParseOutput}>
              Parse output
            </button>
          </div>
          <textarea
            className="textarea mt-4 min-h-[240px] font-mono text-xs"
            value={perplexityOutput}
            onChange={(event) => setPerplexityOutput(event.target.value)}
            placeholder="Paste Perplexity output here..."
          />
        </section>

        <section className="card p-6">
          <div className="flex items-center justify-between">
            <h2 className="section-title">English article fields</h2>
            <span className="badge">Parsed</span>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="subtle">Title</span>
              <input
                className="input"
                value={article.title}
                onChange={(event) => setArticle({ ...article, title: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Description</span>
              <input
                className="input"
                value={article.description}
                onChange={(event) => setArticle({ ...article, description: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Slug</span>
              <div className="flex gap-2">
                <input
                  className="input"
                  value={article.slug}
                  onChange={(event) => setArticle({ ...article, slug: event.target.value })}
                />
                <button
                  className="btn btn-ghost"
                  onClick={() => setArticle({ ...article, slug: slugify(article.title) })}
                >
                  Auto-slug
                </button>
              </div>
            </label>
            <label className="space-y-2">
              <span className="subtle">Category</span>
              <input
                className="input"
                value={article.category}
                onChange={(event) => setArticle({ ...article, category: event.target.value })}
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Tags (comma-separated)</span>
              <input
                className="input"
                value={article.tags.join(', ')}
                onChange={(event) =>
                  setArticle({
                    ...article,
                    tags: event.target.value.split(',').map((tag) => tag.trim()).filter(Boolean)
                  })
                }
              />
            </label>
            <label className="space-y-2">
              <span className="subtle">Translation key</span>
              <div className="flex gap-2">
                <input
                  className="input"
                  value={translationKey}
                  onChange={(event) => setTranslationKey(event.target.value)}
                />
                <button
                  className="btn btn-ghost"
                  onClick={() => setTranslationKey(generateTranslationKey(article.title))}
                >
                  Generate
                </button>
              </div>
            </label>
          </div>
          <label className="mt-4 block space-y-2">
            <span className="subtle">Content (MDX/Markdown)</span>
            <textarea
              className="textarea min-h-[220px] font-mono text-xs"
              value={article.content}
              onChange={(event) => setArticle({ ...article, content: event.target.value })}
            />
          </label>
          <label className="mt-4 block space-y-2">
            <span className="subtle">FAQ</span>
            <textarea
              className="textarea min-h-[120px] font-mono text-xs"
              value={article.faq}
              onChange={(event) => setArticle({ ...article, faq: event.target.value })}
            />
          </label>
        </section>

        <section className="card p-6">
          <div className="flex items-center justify-between">
            <h2 className="section-title">EN Article Package</h2>
            <div className="flex gap-2">
              <button className="btn btn-outline" onClick={() => handleCopy(payloadJson)}>
                Copy JSON
              </button>
              <button className="btn btn-primary" onClick={handleSavePackage}>
                Save JSON
              </button>
              <button className="btn btn-ghost" onClick={openExportsFolder}>
                Open folder
              </button>
            </div>
          </div>
          <textarea className="textarea mt-4 min-h-[260px] font-mono text-xs" value={payloadJson} readOnly />
        </section>
      </div>
    </div>
  );
};

export default App;
