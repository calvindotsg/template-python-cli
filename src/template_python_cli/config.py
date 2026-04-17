"""Configuration loading: defaults.toml -> user TOML -> TEMPLATE_PYTHON_CLI_* env vars."""

from __future__ import annotations

import importlib.resources
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

_xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
DEFAULT_CONFIG_DIR = Path(_xdg) / "template-python-cli"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"


def _load_defaults() -> dict:
    text = (
        importlib.resources.files("template_python_cli")
        .joinpath("defaults.toml")
        .read_text(encoding="utf-8")
    )
    return tomllib.loads(text)


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _apply_env_overrides(data: dict) -> dict:
    """Apply TEMPLATE_PYTHON_CLI_* env var overrides.

    Mapping: TEMPLATE_PYTHON_CLI_SECTION_KEY=value -> data[section][key] = value
    """
    prefix = "TEMPLATE_PYTHON_CLI_"
    for env_key, env_val in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        parts = env_key[len(prefix) :].lower().split("_", 1)
        if len(parts) != 2:
            continue
        section, key = parts
        if section not in data:
            continue
        if not isinstance(data[section], dict):
            continue

        if env_val.lower() in ("true", "false"):
            data[section][key] = env_val.lower() == "true"
        else:
            try:
                data[section][key] = int(env_val)
            except ValueError:
                try:
                    data[section][key] = float(env_val)
                except ValueError:
                    data[section][key] = env_val

    return data


@dataclass
class Config:
    """template-python-cli configuration loaded from 3-layer merge."""

    # [general]
    greeting: str = "Hello"
    verbose: bool = False

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH) -> Config:
        """Load config from 3-layer merge: defaults -> user TOML -> env vars."""
        defaults = _load_defaults()

        user_data: dict = {}
        if path.is_file():
            with open(path, "rb") as f:
                user_data = tomllib.load(f)

        merged = _deep_merge(defaults, user_data)
        merged = _apply_env_overrides(merged)

        return cls._from_dict(merged)

    @classmethod
    def _from_dict(cls, data: dict) -> Config:
        general = data.get("general", {})
        return cls(
            greeting=general.get("greeting", "Hello"),
            verbose=general.get("verbose", False),
        )
