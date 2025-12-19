import React from 'react';
import { GlobalFields } from '@python-blogger/shared';
import { InternalSources, TranslatorSettings } from '../core/models';

interface SettingsPageProps {
  global: GlobalFields;
  settings: TranslatorSettings;
  internalSources: InternalSources;
  onUpdateGlobal: (global: GlobalFields) => void;
  onUpdateSettings: (settings: TranslatorSettings) => void;
  onUpdateSources: (sources: InternalSources) => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({
  global,
  settings,
  internalSources,
  onUpdateGlobal,
  onUpdateSettings,
  onUpdateSources
}) => {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Settings</h2>
        <p className="subtle">Global metadata and anti-thin rules.</p>
      </div>

      <section className="card p-6">
        <h3 className="section-title">Global metadata</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="subtle">Translation key</span>
            <input
              className="input"
              value={global.translationKey}
              onChange={(event) => onUpdateGlobal({ ...global, translationKey: event.target.value })}
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Author</span>
            <input
              className="input"
              value={global.author}
              onChange={(event) => onUpdateGlobal({ ...global, author: event.target.value })}
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Date (YYYY-MM-DD)</span>
            <input
              className="input"
              value={global.date}
              onChange={(event) => onUpdateGlobal({ ...global, date: event.target.value })}
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Updated (optional)</span>
            <input
              className="input"
              value={global.updated || ''}
              onChange={(event) => onUpdateGlobal({ ...global, updated: event.target.value })}
            />
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={global.affiliateDisclosure}
              onChange={(event) =>
                onUpdateGlobal({ ...global, affiliateDisclosure: event.target.checked })
              }
            />
            <span className="subtle">Affiliate disclosure enabled</span>
          </label>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="subtle">Editorial intent</span>
            <input
              className="input"
              value={global.editorialIntent}
              onChange={(event) => onUpdateGlobal({ ...global, editorialIntent: event.target.value })}
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Persona</span>
            <input
              className="input"
              value={global.persona}
              onChange={(event) => onUpdateGlobal({ ...global, persona: event.target.value })}
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Differentiation hook</span>
            <input
              className="input"
              value={global.differentiationHook}
              onChange={(event) =>
                onUpdateGlobal({ ...global, differentiationHook: event.target.value })
              }
            />
          </label>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={global.trustMode}
              onChange={(event) => onUpdateGlobal({ ...global, trustMode: event.target.checked })}
            />
            <span className="subtle">Trust & accuracy mode</span>
          </label>
        </div>
      </section>

      <section className="card p-6">
        <h3 className="section-title">Anti-thin rules</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <label className="space-y-2">
            <span className="subtle">Minimum word count</span>
            <input
              className="input"
              type="number"
              min={200}
              value={settings.minWordCount}
              onChange={(event) =>
                onUpdateSettings({ ...settings, minWordCount: Number(event.target.value) })
              }
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Minimum H2 count</span>
            <input
              className="input"
              type="number"
              min={1}
              value={settings.minH2Count}
              onChange={(event) =>
                onUpdateSettings({ ...settings, minH2Count: Number(event.target.value) })
              }
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Min words per H2</span>
            <input
              className="input"
              type="number"
              min={50}
              value={settings.minWordsPerH2}
              onChange={(event) =>
                onUpdateSettings({ ...settings, minWordsPerH2: Number(event.target.value) })
              }
            />
          </label>
        </div>
      </section>

      <section className="card p-6">
        <h3 className="section-title">Internal link sources</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="subtle">Existing posts list (one per line)</span>
            <textarea
              className="textarea min-h-[150px]"
              value={internalSources.posts.join('\n')}
              onChange={(event) =>
                onUpdateSources({
                  ...internalSources,
                  posts: event.target.value.split('\n').map((item) => item.trim()).filter(Boolean)
                })
              }
            />
          </label>
          <label className="space-y-2">
            <span className="subtle">Existing categories list (one per line)</span>
            <textarea
              className="textarea min-h-[150px]"
              value={internalSources.categories.join('\n')}
              onChange={(event) =>
                onUpdateSources({
                  ...internalSources,
                  categories: event.target.value
                    .split('\n')
                    .map((item) => item.trim())
                    .filter(Boolean)
                })
              }
            />
          </label>
        </div>
      </section>
    </div>
  );
};

export default SettingsPage;
