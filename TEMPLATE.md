# Template Setup Guide

This repository is a GitHub template for bootstrapping Python CLI projects. Follow these steps after creating a new repo from this template.

## Prerequisites

- [`gh`](https://cli.github.com/) — GitHub CLI, authenticated as `calvindotsg`
- [`uv`](https://docs.astral.sh/uv/) — Python package manager
- `git`
- Python 3.11+

## Create from Template

```bash
gh repo create calvindotsg/my-tool \
  --template calvindotsg/template-python-cli \
  --public --clone
cd my-tool
```

## Initialize

```bash
bash scripts/init.sh <tool-name> "<description>" [author]
```

`init.sh` will:
1. Substitute all placeholder values (`template-python-cli`, `template_python_cli`, `TEMPLATE_PYTHON_CLI`, `{{TOKEN}}` markers)
2. Rename `src/template_python_cli/` → `src/<tool_slug>/`
3. Strip the release.yml CI guard (`if: github.repository != ...`)
4. Remove this file and the `scripts/` directory
5. Regenerate `uv.lock`
6. Commit everything

## Post-Init Checklist

### Repository settings

```bash
bash /path/to/.github/scripts/setup-repo.sh calvindotsg/<tool-name>
gh repo edit calvindotsg/<tool-name> \
  --homepage "https://pypi.org/project/<tool-name>/" \
  --add-topic python --add-topic cli
```

### Branch protection

Add required status checks `test (3.11)`, `test (3.12)`, `test (3.13)` via GitHub Rulesets.

### GitHub App (release-please)

Configure in repo **Settings → Secrets and variables → Actions**:
- Variable: `RELEASE_PLEASE_APP_ID`
- Secret: `RELEASE_PLEASE_PRIVATE_KEY`

### PyPI OIDC trusted publisher

At [pypi.org](https://pypi.org/manage/account/publishing/), add a trusted publisher:
- **Owner**: `calvindotsg`
- **Repository**: `<tool-name>`
- **Workflow**: `release.yml`
- **Environment**: `pypi`

### First release

```bash
git commit --allow-empty -m "feat: initial release"
git push
```

release-please will open a release PR on the next push to `main`. Merge it to publish to PyPI and dispatch the Homebrew tap update.
