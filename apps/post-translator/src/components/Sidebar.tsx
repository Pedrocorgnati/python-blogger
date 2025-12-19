import React from 'react';

export type PageKey =
  | 'import'
  | 'affiliate'
  | 'prompts'
  | 'validation'
  | 'translation'
  | 'export'
  | 'settings';

const NAV_ITEMS: { key: PageKey; label: string }[] = [
  { key: 'import', label: 'Import EN Package' },
  { key: 'affiliate', label: 'Affiliate Links' },
  { key: 'prompts', label: 'Prompts' },
  { key: 'validation', label: 'Validation' },
  { key: 'translation', label: 'Translation Check' },
  { key: 'export', label: 'Export' },
  { key: 'settings', label: 'Settings' }
];

interface SidebarProps {
  current: PageKey;
  onNavigate: (page: PageKey) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ current, onNavigate }) => {
  return (
    <aside className="glass flex h-full w-64 flex-col gap-6 p-6">
      <div>
        <div className="text-xs uppercase tracking-[0.3em] text-white/50">post-translator</div>
        <h1 className="text-2xl font-semibold text-white">Localization Studio</h1>
      </div>
      <nav className="flex flex-1 flex-col gap-2">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            className={`flex items-center justify-between rounded-2xl px-4 py-3 text-left text-sm transition ${
              current === item.key
                ? 'bg-white/15 text-white'
                : 'text-white/60 hover:bg-white/10 hover:text-white'
            }`}
            onClick={() => onNavigate(item.key)}
          >
            <span>{item.label}</span>
            {current === item.key && <span className="text-xs text-coral">●</span>}
          </button>
        ))}
      </nav>
      <div className="rounded-2xl bg-white/5 p-4 text-xs text-white/60">
        <p className="font-medium text-white">EN → PT/ES/IT localization</p>
        <p className="mt-1">Import EN package, generate prompts, validate, export.</p>
      </div>
    </aside>
  );
};

export default Sidebar;
