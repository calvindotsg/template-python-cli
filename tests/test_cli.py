from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from template_python_cli.cli import app
from template_python_cli.config import Config
from tests.fixtures import make_config

runner = CliRunner()


@pytest.fixture(autouse=True)
def patch_config_load(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Config, "load", lambda *_a, **_kw: make_config())


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.startswith("template-python-cli ")


def test_help_contains_epilog() -> None:
    result = runner.invoke(app, ["--help"])
    assert "Exit codes:" in result.output
    assert "Examples:" in result.output


def test_hello_default() -> None:
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, world!" in result.output


def test_hello_name() -> None:
    result = runner.invoke(app, ["hello", "--name", "alice"])
    assert result.exit_code == 0
    assert "Hello, alice!" in result.output


def test_hello_dry_run() -> None:
    result = runner.invoke(app, ["hello", "--dry-run"])
    assert result.exit_code == 0
    assert result.output.startswith("[dry-run] would print:")


def test_hello_json() -> None:
    result = runner.invoke(app, ["hello", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert "greeting" in data


def test_hello_empty_name_exits_2() -> None:
    result = runner.invoke(app, ["hello", "--name", ""])
    assert result.exit_code == 2
    assert "Error:" in result.output


def test_runtime_error_exits_1(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_a: object, **_kw: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(Config, "load", _raise)
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 1
    assert "Error:" in result.output
