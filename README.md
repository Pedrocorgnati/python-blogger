# python-blogger monorepo

This repo contains two separate desktop applications built with Tauri + React + TypeScript.

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
