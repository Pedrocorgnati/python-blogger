import React, { useState } from 'react';
import { Locale } from '@python-blogger/shared';

interface PromptsPageProps {
  prompts: Record<Locale, string>;
  blocked: boolean;
  onGenerate: (locale?: Locale) => void;
  onCopy: (locale: Locale) => void;
  onSave: (locale: Locale) => void;
}

const locales: Locale[] = ['pt', 'es', 'it'];

const PromptsPage: React.FC<PromptsPageProps> = ({ prompts, blocked, onGenerate, onCopy, onSave }) => {
  const [active, setActive] = useState<Locale>('pt');

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Localization prompts</h2>
        <p className="subtle">Generate SEO localization prompts for PT/ES/IT.</p>
      </div>

      <section className="card p-6">
        <div className="flex flex-wrap gap-2">
          <button className="btn btn-ghost" onClick={() => onGenerate('pt')} disabled={blocked}>
            Generate PT prompt
          </button>
          <button className="btn btn-ghost" onClick={() => onGenerate('es')} disabled={blocked}>
            Generate ES prompt
          </button>
          <button className="btn btn-ghost" onClick={() => onGenerate('it')} disabled={blocked}>
            Generate IT prompt
          </button>
          <button className="btn btn-primary" onClick={() => onGenerate()} disabled={blocked}>
            Generate ALL
          </button>
        </div>
        {blocked && (
          <p className="mt-3 text-xs text-coral">Import a valid EN package to enable prompts.</p>
        )}
        <div className="mt-6 flex gap-2">
          {locales.map((locale) => (
            <button
              key={locale}
              className={`rounded-full px-4 py-2 text-sm ${
                active === locale ? 'bg-white/20 text-white' : 'text-white/60 hover:text-white'
              }`}
              onClick={() => setActive(locale)}
            >
              {locale.toUpperCase()}
            </button>
          ))}
        </div>
        <textarea
          className="textarea mt-4 min-h-[360px] font-mono text-xs"
          value={prompts[active] || ''}
          readOnly
        />
        <div className="mt-4 flex gap-2">
          <button className="btn btn-outline" onClick={() => onCopy(active)} disabled={!prompts[active]}>
            Copy
          </button>
          <button className="btn btn-ghost" onClick={() => onSave(active)} disabled={!prompts[active]}>
            Save to file
          </button>
        </div>
      </section>
    </div>
  );
};

export default PromptsPage;
