from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable, Optional

try:  # pragma: no cover - optional until PostgreSQL is used
    import psycopg2  # type: ignore
except Exception:  # noqa: S110 - acceptable for optional dependency
    psycopg2 = None  # type: ignore[assignment]

from config.settings import get_settings, database_dsn


class Database:
    """Clase unificada para manejar conexiones y queries en SQLite o PostgreSQL."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.conn: Optional[Any] = None

    def connect(self) -> None:
        """Establece la conexión según el motor configurado."""
        if self.conn:
            return
        logging.getLogger(__name__).info("Connecting DB: %s", database_dsn())
        if self.settings.db_engine == "sqlite":
            self.settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.settings.sqlite_path)
        elif self.settings.db_engine == "postgresql":
            if psycopg2 is None:
                raise RuntimeError("psycopg2-binary is required for PostgreSQL engine")
            self.conn = psycopg2.connect(
                host=self.settings.db_host,
                port=self.settings.db_port,
                user=self.settings.db_user,
                password=self.settings.db_password,
                dbname=self.settings.db_name,
            )
        else:
            raise ValueError(f"Motor de base de datos no soportado: {self.settings.db_engine}")
        self.conn.row_factory = sqlite3.Row if self.settings.db_engine == "sqlite" else None

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    @contextmanager
    def cursor(self):
        """Context manager para abrir/cerrar el cursor automáticamente."""
        if not self.conn:
            self.connect()
        assert self.conn is not None
        cur = self.conn.cursor()
        try:
            yield cur
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    # --- Métodos de ayuda ---
    def execute(self, query: str, params: Optional[Iterable[Any]] = None) -> None:
        with self.cursor() as cur:
            cur.execute(query, params or [])

    def fetch_one(self, query: str, params: Optional[Iterable[Any]] = None) -> Optional[dict]:
        with self.cursor() as cur:
            cur.execute(query, params or [])
            row = cur.fetchone()
            return dict(row) if row is not None and self.settings.db_engine == "sqlite" else row

    def fetch_all(self, query: str, params: Optional[Iterable[Any]] = None) -> list[dict]:
        with self.cursor() as cur:
            cur.execute(query, params or [])
            rows = cur.fetchall()
            if self.settings.db_engine == "sqlite":
                return [dict(r) for r in rows]
            return rows

    # --- Métodos legacy para compatibilidad con issues previos ---
    def execute_query(self, query: str, params: Iterable[Any] | None = None) -> None:
        self.execute(query, params)

