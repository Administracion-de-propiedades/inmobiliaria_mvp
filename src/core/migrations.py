from __future__ import annotations

import logging
from typing import List

from core.database import Database


class MigrationManager:
    """Sistema simple de migraciones compatible con SQLite y PostgreSQL."""

    def __init__(self) -> None:
        self.db = Database()
        self.logger = logging.getLogger(__name__)
        self._ensure_migrations_table()

    def _ensure_migrations_table(self) -> None:
        """Crea la tabla interna de control de migraciones si no existe."""
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute(query)

    def applied_migrations(self) -> List[str]:
        rows = self.db.fetch_all("SELECT name FROM migrations ORDER BY id")
        return [r["name"] for r in rows]

    def apply_migration(self, name: str, sql: str) -> None:
        """Aplica una migración si no fue ejecutada antes."""
        if name in self.applied_migrations():
            self.logger.info(f"✅ Migración '{name}' ya aplicada.")
            return
        self.logger.info(f"🚀 Aplicando migración '{name}'...")
        # Permitir múltiples sentencias separadas por ';' en un mismo archivo
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            self.db.execute(stmt)
        self.db.execute("INSERT INTO migrations (name) VALUES (?)", (name,))
        self.logger.info(f"✅ Migración '{name}' aplicada correctamente.")
