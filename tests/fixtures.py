from __future__ import annotations

from dataclasses import replace

from template_python_cli.config import Config


def make_config(**overrides: object) -> Config:
    """Build a Config with test-default values, allowing per-test overrides."""
    return replace(Config(), **overrides)
