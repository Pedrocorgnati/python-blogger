import React, { useState } from 'react';
import { AffiliateLinks, Locale } from '@python-blogger/shared';

interface AffiliatePageProps {
  affiliate: AffiliateLinks;
  onUpdate: (affiliate: AffiliateLinks) => void;
}

const LOCALES: Locale[] = ['en', 'pt', 'es', 'it'];

const validateUrl = (value: string) => /^https?:\/\//i.test(value.trim());

const AffiliatePage: React.FC<AffiliatePageProps> = ({ affiliate, onUpdate }) => {
  const [status, setStatus] = useState<Record<string, string>>({});

  const updateLocale = (locale: Locale, field: 'primary' | 'secondary' | 'notes', value: string) => {
    const existing = affiliate[locale];
    const updated = {
      ...affiliate,
      [locale]: {
        ...existing,
        [field]:
          field === 'secondary'
            ? value.split(',').map((link) => link.trim()).filter(Boolean).slice(0, 3)
            : value
      }
    };
    onUpdate(updated);
  };

  const checkUrls = (locale: Locale) => {
    const links = affiliate[locale];
    const primaryOk = links.primary ? validateUrl(links.primary) : false;
    const secondaryOk = (links.secondary || []).every((link) => validateUrl(link));
    setStatus((prev) => ({
      ...prev,
      [locale]: primaryOk && secondaryOk ? 'All links look valid.' : 'One or more links are invalid.'
    }));
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Affiliate links</h2>
        <p className="subtle">Provide localized affiliate URLs for each language.</p>
      </div>
      <div className="grid gap-6">
        {LOCALES.map((locale) => (
          <div key={locale} className="card p-6">
            <div className="flex items-center justify-between">
              <h3 className="section-title">{locale.toUpperCase()}</h3>
              <span className="badge">CTA #1 #2 #3</span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="subtle">Primary link</span>
                <input
                  className="input"
                  value={affiliate[locale].primary}
                  onChange={(event) => updateLocale(locale, 'primary', event.target.value)}
                />
              </label>
              <label className="space-y-2">
                <span className="subtle">Secondary links (comma-separated, up to 3)</span>
                <input
                  className="input"
                  value={(affiliate[locale].secondary || []).join(', ')}
                  onChange={(event) => updateLocale(locale, 'secondary', event.target.value)}
                />
              </label>
            </div>
            <label className="mt-4 block space-y-2">
              <span className="subtle">Notes</span>
              <textarea
                className="textarea min-h-[120px]"
                value={affiliate[locale].notes || ''}
                onChange={(event) => updateLocale(locale, 'notes', event.target.value)}
              />
            </label>
            <div className="mt-4 flex items-center gap-3">
              <button className="btn btn-ghost" onClick={() => checkUrls(locale)}>
                Validate URL format
              </button>
              {status[locale] && <span className="text-xs text-white/70">{status[locale]}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AffiliatePage;
