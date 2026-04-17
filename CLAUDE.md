# CLAUDE.md

> AI agent instructions for `template-python-cli`. Human documentation → [README.md](README.md).

## Quick Commands

```bash
uv sync                              # Install deps + create .venv
uv run ruff check src/ tests/        # Lint
uv run ruff format src/ tests/       # Format
uv run pytest                        # Run tests (with coverage)
uv build                             # Build wheel + sdist
uv run template-python-cli --help    # Smoke test
```

## Architecture

```
src/template_python_cli/
├── __init__.py       # Empty — version via importlib.metadata
├── py.typed          # PEP 561 marker
├── cli.py            # Typer app, signal handlers, commands
├── config.py         # 3-layer config merge
├── defaults.toml     # Bundled defaults (layer 1)
└── utils.py          # InputError, error_message
tests/
├── fixtures.py       # make_config() factory
├── test_cli.py       # CLI tests via CliRunner
├── test_config.py    # Config loading tests
└── test_utils.py     # Unit tests for utils
```

## Key Patterns

### 3-layer config merge

`Config.load()` in `config.py`:
1. Bundled `defaults.toml` via `importlib.resources.files("template_python_cli").joinpath("defaults.toml")`
2. User TOML at `~/.config/template-python-cli/config.toml` (XDG-aware)
3. `TEMPLATE_PYTHON_CLI_SECTION_KEY=value` env vars (e.g. `TEMPLATE_PYTHON_CLI_GENERAL_GREETING=Hi`)

Deep merge at section level. Unknown env vars are silently ignored.

### Signal handling

```python
signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)
```

Registered at module import **before** `app = typer.Typer(...)`. Exit code 130 = 128 + SIGINT.

### importlib.resources

Bundled assets loaded without filesystem assumptions:
```python
importlib.resources.files("template_python_cli").joinpath("defaults.toml").read_text(encoding="utf-8")
```

## Implementation Patterns

### stdout is data, stderr is everything else

- **stdout**: primary result only. For `--json`, a single-line JSON document parseable by `json.loads`. No progress, warnings, or diagnostics.
- **stderr**: all other output — progress, warnings, errors, tracebacks.
- `typer.echo(..., err=True)` for error messages. `logging` configured to `stream=sys.stderr`.

Violation breaks downstream agent pipelines that capture stdout for parsing.

### Exit-code mapping

```python
except InputError as e:
    typer.echo(f"Error: {error_message(e)}", err=True)
    raise typer.Exit(code=2)
except typer.Exit:
    raise                          # Let Typer manage its own exits
except Exception as e:
    typer.echo(f"Error: {error_message(e)}", err=True)
    raise typer.Exit(code=1)
```

`InputError` (invalid user input) → exit 2. Bare `Exception` (runtime failure) → exit 1.

### --json contract

`--json` must emit exactly one line on stdout that `json.loads()` accepts. No trailing text, no progress, no warnings on stdout.

### Version string

Use `importlib.metadata.version("template-python-cli")` — never hardcode the version string.

## Constraints

- Python 3.11+ required (`tomllib` stdlib, `match` statements, type-union syntax)
- `uv.lock` is committed and checked in CI (`uv lock --check`)
- `cli.py` is excluded from coverage measurement (side-effecting module-level code)
- No `sudo` or interactive auth in CI

## Release Process

1. Push conventional commits to `main`
2. release-please opens a release PR (bumps version in `pyproject.toml` + `CHANGELOG.md`)
3. `uv.lock` is auto-updated in the release PR branch by the App bot
4. Merge the PR → GitHub release created → PyPI published (OIDC) → Homebrew tap updated

## Reusable Patterns

- `make_config(**overrides)` in `tests/fixtures.py` — inject test configs via `monkeypatch.setattr(Config, "load", ...)`
- `error_message(err)` in `utils.py` — safe string representation of any exception
