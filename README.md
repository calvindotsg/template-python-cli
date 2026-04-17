<!-- template-usage-block-start -->
> **Template repository** — see [TEMPLATE.md](TEMPLATE.md) for setup instructions.
>
> Run `bash scripts/init.sh <tool-name> "<description>"` after cloning to substitute placeholder values.
<!-- template-usage-block-end -->

# {{TOOL_NAME}}

{{TOOL_DESCRIPTION}}

## Quick Start

| I need to… | Command | Details |
|---|---|---|
| Install | `uv tool install {{TOOL_NAME}}` | Requires Python 3.11+ |
| Run | `{{TOOL_NAME}} hello` | Greet with default name |
| Greet someone | `{{TOOL_NAME}} hello --name alice` | Specify a name |
| Machine-readable output | `{{TOOL_NAME}} hello --json` | Emits JSON on stdout |
| Preview | `{{TOOL_NAME}} hello --dry-run` | No output, shows what would happen |
| Configure | `~/.config/{{TOOL_NAME}}/config.toml` | User config file |
| Show version | `{{TOOL_NAME}} --version` | Print installed version |

## Features

- Greet by name with configurable greeting
- `--json` flag for machine-readable output
- `--dry-run` mode for safe previews
- 3-layer configuration (bundled defaults → user TOML → env vars)
- PyPI OIDC publishing and Homebrew tap dispatch on release

## Install

```bash
# via uv
uv tool install {{TOOL_NAME}}

# via Homebrew (after tap setup)
brew install calvindotsg/tap/{{TOOL_NAME}}
```

## Usage

```
{{TOOL_NAME}} hello [OPTIONS]

Options:
  --name TEXT     Name to greet.  [default: world]
  --dry-run       Preview without output.
  --verbose       Enable verbose logging.
  --json          Emit JSON on stdout.
  --help          Show this message and exit.
```

**Exit codes:** 0 success · 1 runtime error · 2 invalid input · 130 interrupted

## Configuration

{{TOOL_NAME}} uses a 3-layer configuration merge:

1. **Bundled defaults** (`defaults.toml` — always present)
2. **User config** (`~/.config/{{TOOL_NAME}}/config.toml` — optional overrides)
3. **Environment variables** (`TEMPLATE_PYTHON_CLI_SECTION_KEY=value`)

```toml
# ~/.config/{{TOOL_NAME}}/config.toml
[general]
greeting = "Hello"
verbose = false
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
