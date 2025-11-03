from __future__ import annotations

import logging
import sqlite3
from typing import Any, Iterable, Optional

from config.settings import get_settings, database_dsn


class Database:
    """Database wrapper using typed settings.

    - SQLite supported now.
    - PostgreSQL left as TODO with psycopg2.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._engine: str = self._settings.db_engine
        self._conn: Optional[Any] = None

    def _log_dsn(self) -> None:
        dsn = database_dsn()
        logging.getLogger(__name__).info("DB connection target: %s", dsn)

    def connect(self) -> Any:
        if self._conn is None:
            self._log_dsn()
            if self._engine == "sqlite":
                # Ensure parent directory exists
                self._settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(self._settings.sqlite_path.as_posix())
                conn.row_factory = sqlite3.Row
                self._conn = conn
            elif self._engine == "postgresql":  # pragma: no cover - placeholder
                # TODO: Implement psycopg2 connection using values from get_settings()
                raise NotImplementedError("PostgreSQL connection not implemented yet")
            else:
                raise ValueError(f"Unsupported DB engine: {self._engine}")
        return self._conn

    def execute_query(self, query: str, params: Iterable[Any] | None = None) -> None:
        conn = self.connect()
        with conn:
            conn.execute(query, tuple(params or ()))

    def fetch_all(self, query: str, params: Iterable[Any] | None = None) -> list[Any]:
        conn = self.connect()
        cur = conn.execute(query, tuple(params or ()))
        return list(cur.fetchall())

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

