from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional


class Database:
    """Simple SQLite database wrapper prepared for future PostgreSQL support.

    This class centralizes DB access for the app. For now it uses SQLite with
    a single file database. In the future, a strategy can be added to switch
    to PostgreSQL while keeping the same interface.
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize the database wrapper.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path: Path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Open a connection to the SQLite database if not already open.

        Returns:
            The active SQLite connection.
        """
        if self._conn is None:
            # Ensure folder exists; SQLite will create the file automatically.
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self._db_path.as_posix())
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def execute_query(self, query: str, params: Iterable[Any] | None = None) -> None:
        """Execute a write (DDL/DML) query and commit.

        Args:
            query: SQL statement to execute.
            params: Parameters for the SQL statement.
        """
        conn = self.connect()
        with conn:  # Context manager commits/rollbacks automatically
            conn.execute(query, tuple(params or ()))

    def fetch_all(self, query: str, params: Iterable[Any] | None = None) -> list[sqlite3.Row]:
        """Execute a read-only query and fetch all rows.

        Args:
            query: SQL SELECT statement.
            params: Parameters for the SQL statement.

        Returns:
            List of rows as sqlite3.Row items.
        """
        conn = self.connect()
        cur = conn.execute(query, tuple(params or ()))
        return list(cur.fetchall())

    def close(self) -> None:
        """Close the active DB connection, if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

