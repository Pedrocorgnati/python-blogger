import React from 'react';
import { TranslationValidation } from '../core/models';

interface ValidationPageProps {
  reports: TranslationValidation[];
  minWordCount: number;
  minH2Count: number;
  minWordsPerH2: number;
}

const ValidationPage: React.FC<ValidationPageProps> = ({
  reports,
  minWordCount,
  minH2Count,
  minWordsPerH2
}) => {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Validation</h2>
        <p className="subtle">Quality gates applied to localized outputs.</p>
      </div>

      <section className="card p-6">
        <h3 className="section-title">Rules snapshot</h3>
        <div className="mt-4 grid gap-3 text-sm text-white/70 md:grid-cols-3">
          <div>Minimum words: {minWordCount}</div>
          <div>Minimum H2: {minH2Count}</div>
          <div>Min words per H2: {minWordsPerH2}</div>
        </div>
      </section>

      <section className="card p-6">
        <h3 className="section-title">Locale status</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {reports.map((report) => (
            <div key={report.locale} className="rounded-2xl bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">{report.locale.toUpperCase()}</span>
                <span className="badge">{report.status.toUpperCase()}</span>
              </div>
              <p className="mt-2 text-xs text-white/60">
                {report.issues.length === 0 ? 'All checks passed.' : `${report.issues.length} issue(s).`}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default ValidationPage;
