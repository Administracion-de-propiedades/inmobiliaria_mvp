from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _base_dir() -> Path:
    """Project root directory (parent of `src`).

    This works when running `python src/app.py`.
    """
    return Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class Settings:
    """App settings container."""

    APP_TITLE: str
    DB_PATH: Path


settings = Settings(
    APP_TITLE="Inmobiliaria MVP",
    DB_PATH=_base_dir() / "database.db",
)

