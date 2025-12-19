# python-blogger monorepo

This repo contains two separate desktop applications built with Tauri + React + TypeScript.
It also contains a Python editorial pipeline with Creator → Translator → Distributor.

## Apps

### post-creator

Purpose: build a Perplexity prompt to generate an English article, then export a clean EN Article Package JSON.

Responsibilities:
- Generate Perplexity prompts (English only)
- Parse Perplexity output into structured fields
- Export EN Article Package JSON

### post-translator

Purpose: localize an English article package into PT/ES/IT and export publish-ready payloads.

Responsibilities:
- Import EN Article Package
- Generate localization prompts
- Validate translated outputs
- Export Admin Publish Payload + MDX skeletons

## Workflow

1. Open `post-creator` and build the Perplexity prompt.
2. Paste Perplexity output, parse, and export EN Article Package JSON.
3. Open `post-translator` and import the EN package.
4. Generate PT/ES/IT prompts, paste localized outputs, validate.
5. Export Admin Publish Payload + MDX skeletons.

## Python pipeline (Theme Generator → Creator → Translator → Distributor)

Only the Distributor has a full UI in the Python pipeline; Creator/Translator are minimal UIs.

Run each app (from the app folder):

```bash
cd creator-app
python -m venv .venv
pip install -r requirements.txt
python src/main.py

cd ../translator-app
python -m venv .venv
pip install -r requirements.txt
python src/main.py

cd ../distribution-prompt-builder
python -m venv .venv
pip install -r requirements.txt
python src/main.py
```

Run each app (from the monorepo root):

```bash
python apps/desktop/python-blogger/creator-app/src/main.py
python apps/desktop/python-blogger/translator-app/src/main.py
python apps/desktop/python-blogger/distribution-prompt-builder/src/main.py
```

Windows (PowerShell):

```powershell
python apps/desktop/python-blogger/creator-app/src/main.py
python apps/desktop/python-blogger/translator-app/src/main.py
python apps/desktop/python-blogger/distribution-prompt-builder/src/main.py
```

Pipeline flow:
1. Theme Generator (Creator app) defines the Theme.
2. Creator exports `outputs/content-packages/<translationKey>-creator.json`.
3. Translator imports it, fills PT/ES/IT, exports `outputs/content-packages/<translationKey>-translator.json`.
4. Distributor imports it, generates channel prompts and exports bundles + results templates.

Theme Generator:
- Import latest themes from `content/posts/en/*.mdx`.
- Generate a Perplexity prompt and paste results to pick a Theme.

Schema:
`<repo_root>/schemas/content_package.schema.json`

Schema resolution:
- Apps locate the repo root by walking up from their `src/` folder.
- If the repo root is not found, they fall back to a local `schemas/` folder (dev only) and log a warning.

Storage (per app):
- Outputs: `<app_root>/outputs/`
- Drafts/data: `<app_root>/data/`
- Logs: `<app_root>/logs/errors.log`

Mocks (for quick testing):
- `mock_creator/generate_sample.py`
- `mock_translator/generate_sample.py`

Smoke test:
- `python apps/desktop/python-blogger/scripts/smoke_test.py`

## Monorepo structure

```
/apps
  /post-creator
  /post-translator
/packages
  /shared
```

## Scripts (root)

```bash
pnpm install
pnpm creator:dev
pnpm translator:dev
pnpm creator:build
pnpm translator:build
```

## Local files (AppData)

All files are stored under each app's Tauri AppData directory:

post-creator:
- `outputs/shared/en-packages/<translationKey>.json`

post-translator:
- `outputs/prompts/<translationKey>-<locale>.txt`
- `exports/<translationKey>-payload.json`
- `exports/mdx/<locale>/<slug>.mdx`
