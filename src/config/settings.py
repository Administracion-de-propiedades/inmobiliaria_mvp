from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Optional .env loader; keeps runtime working even if python-dotenv isn't installed.
try:  # pragma: no cover - best-effort optional dependency
    from dotenv import load_dotenv  # type: ignore
except Exception:  # noqa: S110 - broad except acceptable for optional dep
    load_dotenv = None  # type: ignore[assignment]


def _base_dir() -> Path:
    """Project root directory (parent of `src`)."""
    return Path(__file__).resolve().parents[2]


# Load environment variables from a .env file at project root if available.
_DOTENV_PATH = _base_dir() / ".env"
if load_dotenv is not None and _DOTENV_PATH.exists():  # pragma: no cover - env side effect
    load_dotenv(_DOTENV_PATH)


@dataclass(slots=True)
class Settings:
    """App settings container."""

    APP_TITLE: str

    # Database configuration
    DB_ENGINE: str  # "sqlite" or "postgresql"
    DB_NAME: str
    DB_HOST: str | None
    DB_PORT: int | None
    DB_USER: str | None
    DB_PASSWORD: str | None

    # Security / app secrets
    SECRET_KEY: str

    # Base directory for relative paths
    BASE_DIR: Path

    @property
    def SQLITE_PATH(self) -> Path:
        """Absolute path to SQLite database file.

        If `DB_NAME` is relative, it is considered relative to `BASE_DIR`.
        """
        db_name = self.DB_NAME
        p = Path(db_name)
        return p if p.is_absolute() else (self.BASE_DIR / db_name)


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None:
        return None
    return value.strip()


def _get_env_int(name: str) -> int | None:
    raw = _get_env(name)
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except ValueError:
        return None


settings = Settings(
    APP_TITLE="Inmobiliaria MVP",
    DB_ENGINE=_get_env("DB_ENGINE", "sqlite").lower() if _get_env("DB_ENGINE") else "sqlite",
    DB_NAME=_get_env("DB_NAME", "database.db") or "database.db",
    DB_HOST=_get_env("DB_HOST"),
    DB_PORT=_get_env_int("DB_PORT"),
    DB_USER=_get_env("DB_USER"),
    DB_PASSWORD=_get_env("DB_PASSWORD"),
    SECRET_KEY=_get_env("SECRET_KEY", "clave-super-secreta") or "clave-super-secreta",
    BASE_DIR=_base_dir(),
)


