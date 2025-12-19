# translator-app

UI mínima para importar o pacote do Creator, preencher PT/ES/IT e exportar o pacote completo e o pacote do Blog Admin.

## Run

```bash
python -m venv .venv
pip install -r requirements.txt
python src/main.py
```

Run from the monorepo root (after installing deps):

```bash
python apps/desktop/python-blogger/translator-app/src/main.py
```

Schema:
`<repo_root>/schemas/content_package.schema.json`

## Outputs

- Drafts: `data/drafts/<translationKey>-translator.json`
- Export: `outputs/content-packages/<translationKey>-translator.json`
- Blog Admin: `outputs/blog-admin/<translationKey>-blog-admin.json`
- Logs: `logs/errors.log`
