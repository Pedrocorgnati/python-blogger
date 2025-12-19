import React from 'react';

interface ExportPageProps {
  payloadJson: string;
  blocked: boolean;
  onCopy: () => void;
  onSave: () => void;
  onExportMdx: () => void;
  onOpenExports: () => void;
}

const ExportPage: React.FC<ExportPageProps> = ({
  payloadJson,
  blocked,
  onCopy,
  onSave,
  onExportMdx,
  onOpenExports
}) => {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold text-white">Export</h2>
        <p className="subtle">Generate admin payload JSON and MDX skeletons.</p>
      </div>

      <section className="card p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h3 className="section-title">Admin Publish Payload</h3>
          <div className="flex gap-2">
            <button className="btn btn-outline" onClick={onCopy}>
              Copy JSON
            </button>
            <button className="btn btn-ghost" onClick={onSave} disabled={blocked}>
              Save JSON
            </button>
          </div>
        </div>
        <textarea className="textarea mt-4 min-h-[320px] font-mono text-xs" value={payloadJson} readOnly />
      </section>

      <section className="card p-6">
        <h3 className="section-title">MDX exports</h3>
        <p className="subtle mt-1">Create MDX skeleton files per locale in exports/mdx.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <button className="btn btn-primary" onClick={onExportMdx} disabled={blocked}>
            Export MDX files
          </button>
          <button className="btn btn-outline" onClick={onOpenExports}>
            Open exports folder
          </button>
        </div>
        {blocked && (
          <p className="mt-3 text-xs text-coral">Resolve validation failures to enable export.</p>
        )}
      </section>
    </div>
  );
};

export default ExportPage;
