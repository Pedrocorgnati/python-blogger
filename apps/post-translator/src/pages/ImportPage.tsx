import React, { useState } from 'react';
import { EnglishArticlePackage } from '@python-blogger/shared';

interface ImportPageProps {
  enPackage: EnglishArticlePackage | null;
  onImportJson: (value: string) => void;
  onOpenFile: () => void;
}

const ImportPage: React.FC<ImportPageProps> = ({ enPackage, onImportJson, onOpenFile }) => {
  const [jsonInput, setJsonInput] = useState('');

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Import EN Article Package</h2>
        <p className="subtle">Paste or load the JSON created by post-creator.</p>
      </div>

      <section className="card p-6">
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn btn-primary" onClick={onOpenFile}>
            Open JSON file
          </button>
          <button className="btn btn-ghost" onClick={() => onImportJson(jsonInput)}>
            Import from paste
          </button>
        </div>
        <textarea
          className="textarea mt-4 min-h-[220px] font-mono text-xs"
          value={jsonInput}
          onChange={(event) => setJsonInput(event.target.value)}
          placeholder="Paste EN Article Package JSON here..."
        />
      </section>

      {enPackage && (
        <section className="card p-6">
          <div className="flex items-center justify-between">
            <h3 className="section-title">Imported package</h3>
            <span className="badge">{enPackage.global.translationKey}</span>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="subtle">Title</p>
              <p className="text-sm text-white">{enPackage.english.title}</p>
            </div>
            <div>
              <p className="subtle">Slug</p>
              <p className="text-sm text-white">{enPackage.english.slug}</p>
            </div>
            <div>
              <p className="subtle">Category</p>
              <p className="text-sm text-white">{enPackage.english.category}</p>
            </div>
            <div>
              <p className="subtle">Tags</p>
              <p className="text-sm text-white">{enPackage.english.tags.join(', ')}</p>
            </div>
          </div>
          <div className="mt-4">
            <p className="subtle">Description</p>
            <p className="text-sm text-white">{enPackage.english.description}</p>
          </div>
          <div className="mt-4">
            <p className="subtle">FAQ</p>
            <p className="text-sm text-white">{enPackage.english.faq}</p>
          </div>
        </section>
      )}
    </div>
  );
};

export default ImportPage;
