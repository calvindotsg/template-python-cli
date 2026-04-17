from __future__ import annotations

from pathlib import Path

import pytest

from template_python_cli.config import Config, _deep_merge


def test_defaults_only(tmp_path: Path) -> None:
    cfg = Config.load(path=tmp_path / "nonexistent.toml")
    assert cfg.greeting == "Hello"
    assert cfg.verbose is False


def test_user_toml_override(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[general]\ngreeting = "Hi"\n', encoding="utf-8")
    cfg = Config.load(path=config_file)
    assert cfg.greeting == "Hi"


def test_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEMPLATE_PYTHON_CLI_GENERAL_GREETING", "Hey")
    cfg = Config.load(path=tmp_path / "nonexistent.toml")
    assert cfg.greeting == "Hey"


def test_deep_merge_preserves_unrelated_fields() -> None:
    base = {"general": {"greeting": "Hello", "verbose": False}}
    override = {"general": {"verbose": True}}
    merged = _deep_merge(base, override)
    assert merged["general"]["greeting"] == "Hello"
    assert merged["general"]["verbose"] is True


def test_unknown_env_prefix_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNRELATED_VAR", "ignored")
    cfg = Config.load(path=tmp_path / "nonexistent.toml")
    assert cfg.greeting == "Hello"
