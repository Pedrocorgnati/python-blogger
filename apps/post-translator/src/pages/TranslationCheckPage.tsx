import React from 'react';
import { Locale } from '@python-blogger/shared';
import { TranslationValidation } from '../core/models';

interface TranslationCheckPageProps {
  values: Record<Locale, string>;
  reports: TranslationValidation[];
  onChange: (locale: Locale, value: string) => void;
}

const TranslationCheckPage: React.FC<TranslationCheckPageProps> = ({ values, reports, onChange }) => {
  const locales: Locale[] = ['pt', 'es', 'it'];

  const reportByLocale = (locale: Locale) => reports.find((report) => report.locale === locale);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Translation Check</h2>
        <p className="subtle">Paste localized outputs to verify completeness.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {locales.map((locale) => {
          const report = reportByLocale(locale);
          return (
            <div key={locale} className="card p-6">
              <div className="flex items-center justify-between">
                <h3 className="section-title">{locale.toUpperCase()}</h3>
                {report && (
                  <span className="badge">
                    {report.status === 'pass' ? 'OK to publish' : report.status.toUpperCase()}
                  </span>
                )}
              </div>
              <textarea
                className="textarea mt-4 min-h-[320px] font-mono text-xs"
                value={values[locale]}
                onChange={(event) => onChange(locale, event.target.value)}
                placeholder={`Paste ${locale.toUpperCase()} output here...`}
              />
              {report && (
                <ul className="mt-3 space-y-2 text-xs text-white/70">
                  {report.issues.length === 0 && <li>✅ All checks passed.</li>}
                  {report.issues.map((issue, idx) => (
                    <li key={`${locale}-${idx}`}>{issue}</li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TranslationCheckPage;
