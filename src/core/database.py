from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

from config.settings import settings


class Database:
    """Database wrapper that supports SQLite and prepares for PostgreSQL.

    Defaults to SQLite using `DB_NAME` from the environment. If `DB_ENGINE`
    is "postgresql", a psycopg2 connection is created using the remaining
    environment variables.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._engine: str = settings.DB_ENGINE
        self._conn: Optional[Any] = None

        if self._engine == "sqlite":
            # Path to SQLite file (argument overrides env for flexibility)
            self._db_path: Path = db_path or settings.SQLITE_PATH
        else:
            # Store PostgreSQL connection params; connect lazily.
            self._pg_params = {
                "dbname": settings.DB_NAME,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
            }

    def _adapt_query(self, query: str) -> str:
        if self._engine == "postgresql":
            # Very simple placeholder adaptation from SQLite ('?') to psycopg2 ('%s')
            return query.replace("?", "%s")
        return query

    def connect(self) -> Any:
        """Open a connection to the configured database if not already open."""
        if self._conn is None:
            if self._engine == "sqlite":
                # Ensure folder exists; SQLite will create the file automatically.
                self._db_path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(self._db_path.as_posix())
                conn.row_factory = sqlite3.Row
                self._conn = conn
            elif self._engine == "postgresql":
                try:  # Lazy import to avoid hard dependency in SQLite-only setups
                    import psycopg2  # type: ignore
                except Exception as exc:  # pragma: no cover - environment dependent
                    raise RuntimeError("psycopg2 is required for PostgreSQL engine") from exc
                # Drop None values from params
                params = {k: v for k, v in self._pg_params.items() if v is not None}
                self._conn = psycopg2.connect(**params)  # type: ignore[call-arg]
            else:
                raise ValueError(f"Unsupported DB_ENGINE: {self._engine}")
        return self._conn

    def execute_query(self, query: str, params: Iterable[Any] | None = None) -> None:
        """Execute a write (DDL/DML) query and commit."""
        conn = self.connect()
        if self._engine == "sqlite":
            with conn:  # Context manager commits/rollbacks automatically
                conn.execute(query, tuple(params or ()))
        else:
            q = self._adapt_query(query)
            with conn:  # psycopg2 connection context commits on exit
                with conn.cursor() as cur:
                    cur.execute(q, tuple(params or ()))

    def fetch_all(self, query: str, params: Iterable[Any] | None = None) -> list[Any]:
        """Execute a read-only query and fetch all rows."""
        conn = self.connect()
        if self._engine == "sqlite":
            cur = conn.execute(query, tuple(params or ()))
            return list(cur.fetchall())
        q = self._adapt_query(query)
        with conn.cursor() as cur:  # type: ignore[attr-defined]
            cur.execute(q, tuple(params or ()))
            return list(cur.fetchall())

    def close(self) -> None:
        """Close the active DB connection, if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

