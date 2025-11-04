from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

try:  # pragma: no cover - optional import
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - best-effort fallback
    load_dotenv = None  # type: ignore[assignment]


EnvName = Literal["DEV", "PROD", "TEST"]
DbEngine = Literal["sqlite", "postgresql"]


def _base_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    if load_dotenv is None:
        return
    env_path = _base_dir() / ".env"
    if env_path.exists():  # pragma: no cover - side effect
        load_dotenv(env_path)


def get_env_str(key: str, default: str) -> str:
    value = os.environ.get(key)
    return (value if value is not None else default).strip()


def get_env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def get_env_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return default
    val = raw.strip().lower()
    if val in {"1", "true", "yes", "y", "on"}:
        return True
    if val in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(slots=True)
class Config:
    env: EnvName
    app_title: str
    version: str
    db_engine: DbEngine
    db_name: str
    db_host: str | None
    db_port: int | None
    db_user: str | None
    db_password: str | None
    base_dir: Path
    data_dir: Path
    sqlite_path: Path
    log_level: str


def _resolve_sqlite_path(base_dir: Path, data_dir: Path, db_name: str) -> Path:
    p = Path(db_name)
    if p.is_absolute():
        return p
    return (data_dir or base_dir) / p


@lru_cache(maxsize=1)
def get_settings() -> Config:
    """Return a singleton configuration loaded from environment and defaults."""
    _load_dotenv()

    base_dir = _base_dir()
    data_dir = base_dir  # could be customized in future
    data_dir.mkdir(parents=True, exist_ok=True)

    env: EnvName = get_env_str("ENV", "DEV").upper()  # type: ignore[assignment]
    if env not in ("DEV", "PROD", "TEST"):
        env = "DEV"

    db_engine: DbEngine = get_env_str("DB_ENGINE", "sqlite").lower()  # type: ignore[assignment]
    if db_engine not in ("sqlite", "postgresql"):
        db_engine = "sqlite"

    # Support override via APP_DB_PATH for test/alt DB path
    app_db_path = get_env_str("APP_DB_PATH", "")
    db_name = get_env_str("DB_NAME", "database.db")
    db_host = get_env_str("DB_HOST", "").strip() or None
    db_user = get_env_str("DB_USER", "").strip() or None
    db_password = get_env_str("DB_PASSWORD", "").strip() or None
    db_port_val = get_env_str("DB_PORT", "").strip()
    db_port = int(db_port_val) if db_port_val.isdigit() else None

    if db_engine == "postgresql":
        # Basic validation for required fields in PostgreSQL profile
        if not (db_host and db_user and db_password and db_port and db_name):
            raise ValueError("Incomplete PostgreSQL configuration in environment variables")

    # If APP_DB_PATH is provided, prefer it over DB_NAME
    if app_db_path:
        sqlite_path = Path(app_db_path)
    else:
        sqlite_path = _resolve_sqlite_path(base_dir, data_dir, db_name)

    cfg = Config(
        env=env,
        app_title=get_env_str("APP_TITLE", "Inmobiliaria MVP"),
        version=get_env_str("VERSION", "0.1.0"),
        db_engine=db_engine,
        db_name=db_name,
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        base_dir=base_dir,
        data_dir=data_dir,
        sqlite_path=sqlite_path,
        log_level=get_env_str("LOG_LEVEL", "INFO").upper(),
    )
    return cfg


def database_dsn() -> str:
    s = get_settings()
    if s.db_engine == "sqlite":
        return f"sqlite:///{s.sqlite_path}"
    # mask password
    user = s.db_user or ""
    host = s.db_host or ""
    port = f":{s.db_port}" if s.db_port else ""
    return f"postgresql://{user}:***@{host}{port}/{s.db_name}"


def configure_logging() -> None:
    s = get_settings()
    # basicConfig is a no-op if logging is already configured
    logging.basicConfig(level=getattr(logging, s.log_level, logging.INFO))


