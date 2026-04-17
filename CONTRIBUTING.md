# Contributing

## Development Setup

```bash
git clone https://github.com/calvindotsg/template-python-cli
cd template-python-cli
uv sync
```

This installs all runtime and dev dependencies into `.venv/` and generates `uv.lock`.

## Code Style

Ruff for linting and formatting:

```bash
uv run ruff check src/ tests/     # Lint
uv run ruff format src/ tests/    # Format
```

Line length: 100. Target: Python 3.11. Rules: E, F, I, N, W, UP.

## Testing

```bash
uv run pytest                     # Run tests with coverage
uv run pytest -x                  # Stop on first failure
uv run pytest tests/test_cli.py   # Run a specific file
```

Coverage gate: 75% (lines, branches, statements). `cli.py` is excluded from measurement.

## Dependencies

- **Runtime**: `typer>=0.12` (Rich is a transitive dep — zero extra deps)
- **Dev**: `ruff>=0.8`, `pytest>=8`, `pytest-cov>=5`
- **Manager**: uv — never use pip or poetry

To add a dependency:
```bash
uv add <package>          # Runtime
uv add --dev <package>    # Dev-only (adds to [dependency-groups])
```

## Commit Conventions

Conventional Commits v1.0.0. Format: `<type>(<scope>): <description>`

| Type | Description |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `test` | Test additions or changes |
| `docs` | Documentation only |
| `chore` | Maintenance (deps, tooling) |
| `ci` | CI/CD config changes |

**Scope table:**

| Scope | File glob | Description |
|---|---|---|
| `src` | `src/template_python_cli/**` | Library/CLI code |
| `tests` | `tests/**` | Unit tests |
| `ci` | `.github/workflows/**` | CI config |
| `repo` | `.gitignore, .python-version, pyproject.toml metadata` | Repo-level config |
| `docs` | `*.md, docs/**` | Documentation |

Examples:
```
feat(src): add --output flag to hello command
fix(src): handle empty name gracefully
test(tests): add coverage for dry-run path
ci(ci): pin setup-uv to v5
```

## Release Process

Releases are automated via release-please v4:

1. Merge conventional commits to `main`
2. release-please opens a release PR (bumps version + updates `CHANGELOG.md`)
3. `uv.lock` is auto-updated in the release PR branch
4. Merge the PR → GitHub release → PyPI publish (OIDC) → Homebrew tap update

No manual version bumping — the commit history drives versions.

## Repository Setup

For a new repo created from this template, see [TEMPLATE.md](TEMPLATE.md).
