# distribution-prompt-builder

Desktop app to convert an existing EN/PT/ES/IT blog article into channel-native prompts for GPT. It outputs copy-ready posts and (when applicable) Midjourney thumbnail prompts.

## What it does

- Takes article content in EN/PT/ES/IT
- Generates GPT prompts for: Reddit, Quora, Dev.to, Hashnode, LinkedIn, Medium
- Applies anti-spam rules per channel
- Exports prompts as text files for easy copy/paste

## Pipeline overview

Creator → Translator → Distributor

- Creator (mock): generates EN content JSON
- Translator (mock): generates EN + PT/ES/IT JSON
- Distributor (this app): imports JSON and generates channel prompts

Only the Distributor has a full UI right now.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Run from the monorepo root (after installing deps):

```bash
python apps/desktop/python-blogger/distribution-prompt-builder/src/main.py
```

## Workflow

1. Paste EN/PT/ES/IT content (titles/description optional).
2. Choose Distribution Plan (default: Separate accounts per language).
3. Choose channels and style settings.
4. Click Generate posts.
5. Paste prompts into GPT.
6. Use returned text in each channel and language-specific account.

LinkedIn options:
- Generate first comment (default on)
- CTA policy: no links, link in comments, or link at end of post

## JSON schema

The app supports importing a content package JSON validated against:
`<repo_root>/schemas/content_package.schema.json`

Use the mock generator scripts in `mock_creator/` and `mock_translator/` to produce valid JSON for testing.

## Profiles & Bios

The app includes a Profile & Bio Manager to keep identity consistent across channels.

What it stores (per locale and channel):
- short, medium, long bios
- one-liner tagline
- pinned post template
- link policy notes
- dos and donts

How it connects:
- When generating prompts, the correct bio is injected as writer identity.
- Bios are used as voice reference only (not pasted verbatim in posts).

Storage:
- `profile-kit/bios.json` and `profile-kit/bios.md` (inside the app root)
- runtime copy: `data/profiles.json`
- exports: `outputs/profile-kit/`

Base folders (inside the app root):
- Outputs: `outputs/`
- Drafts/data: `data/`
- Logs: `logs/errors.log`

Exports:
- JSON: `outputs/profile-kit/bios.json`
- Markdown: `outputs/profile-kit/bios.md`

## Anti-spam rules (high level)

- Reddit/Quora: reputation first, no selling, avoid affiliate links by default, blog links off unless enabled.
- Dev.to/Hashnode/Medium: editorial tone, blog link allowed in footer, affiliate only with disclosure.
- LinkedIn: hook + scannable format, first comment required, link policy applies.

## Output format (GPT)

Each channel prompt requests:

```
CHANNEL: <name>
=== LOCALE: EN ===
POST_TEXT:
...
THUMBNAIL_PROMPT (MIDJOURNEY):
...
FIRST_COMMENT (LinkedIn only):
...

=== LOCALE: PT ===
...
```

If thumbnails are not allowed for the channel, it must return `N/A`. If not LinkedIn, `FIRST_COMMENT` must be `N/A`.

## Outputs

- All prompts: `outputs/distribution-prompts/<translationKey>-distribution-prompts.txt`
- Per channel bundle: `outputs/distribution-prompts/<translationKey>/<channel>-bundle.txt`
- Results templates: `outputs/distribution-results/<translationKey>/<channel>-results.txt`
