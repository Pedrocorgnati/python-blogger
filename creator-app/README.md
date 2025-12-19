# creator-app

UI mínima para criar o conteúdo original em inglês e exportar um content package JSON compatível com o schema.
Inclui o Theme Generator (etapa 0 do wizard) e placeholders para as próximas etapas.

## Run

```bash
python -m venv .venv
pip install -r requirements.txt
python src/main.py
```

Run from the monorepo root (after installing deps):

```bash
python apps/desktop/python-blogger/creator-app/src/main.py
```

Schema:
`<repo_root>/schemas/content_package.schema.json`

## Outputs

- Drafts: `data/drafts/<translationKey>-creator.json`
- Export: `outputs/content-packages/<translationKey>-creator.json`
- Logs: `logs/errors.log`

Theme Generator drafts:
- `data/drafts/<translationKey-or-timestamp>-theme.json`
