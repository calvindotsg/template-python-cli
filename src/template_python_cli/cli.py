"""template-python-cli — {{TOOL_DESCRIPTION}}"""

from __future__ import annotations

import json as _json
import logging
import signal
import sys
from importlib.metadata import version as pkg_version
from typing import Annotated

import typer

from template_python_cli.config import Config
from template_python_cli.utils import InputError, error_message


def _handle_signal(signum: int, _frame: object) -> None:
    logging.getLogger("template_python_cli").warning("Interrupted (signal %d)", signum)
    sys.exit(130)


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

EPILOG = """Exit codes:
  0   Success
  1   Runtime error
  2   Invalid input
  130 Interrupted (SIGINT/SIGTERM)

Examples:
  template-python-cli hello
  template-python-cli hello --name alice
  template-python-cli hello --dry-run
  template-python-cli hello --json
"""

app = typer.Typer(help="{{TOOL_DESCRIPTION}}", no_args_is_help=True, epilog=EPILOG)


def _version_callback(value: bool) -> None:
    if value:
        try:
            v = pkg_version("template-python-cli")
        except Exception:
            v = "unknown"
        typer.echo(f"template-python-cli {v}")
        raise typer.Exit()


@app.callback()
def main(
    _version: Annotated[
        bool | None,
        typer.Option(
            "--version", "-v", callback=_version_callback, is_eager=True, help="Show version."
        ),
    ] = None,
) -> None:
    """{{TOOL_DESCRIPTION}}"""


@app.command(epilog=EPILOG)
def hello(
    name: Annotated[str, typer.Option("--name", help="Name to greet.")] = "world",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without output.")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Enable verbose logging.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Emit JSON on stdout.")] = False,
) -> None:
    """Greet a name."""
    try:
        if not name:
            raise InputError("--name must be non-empty")
        cfg = Config.load()
        greeting = f"{cfg.greeting}, {name}!"
        if verbose:
            logging.basicConfig(level=logging.INFO, stream=sys.stderr)
            logging.info("hello.name=%s dry_run=%s json=%s", name, dry_run, json_output)
        if dry_run:
            typer.echo(f"[dry-run] would print: {greeting}")
            return
        if json_output:
            typer.echo(_json.dumps({"greeting": greeting}))
            return
        typer.echo(greeting)
    except InputError as e:
        typer.echo(f"Error: {error_message(e)}", err=True)
        raise typer.Exit(code=2)
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error: {error_message(e)}", err=True)
        raise typer.Exit(code=1)
