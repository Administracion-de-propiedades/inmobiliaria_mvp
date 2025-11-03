from __future__ import annotations

from typing import Optional

from core.database import Database
from entities.usuario import Usuario


class UsuarioRepository:
    """Ejemplo de repositorio para la entidad Usuario.

    Para el MVP, la autenticación no consulta la base; esto queda listo para
    una futura persistencia real.
    """

    def __init__(self, db: Database) -> None:
        self._db = db
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._db.execute_query(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )

    def crear(self, usuario: Usuario) -> int:
        self._db.execute_query(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (usuario.username, usuario.password),
        )
        # SQLite lastrowid readback
        row = self._db.fetch_all("SELECT last_insert_rowid() as id")[0]
        return int(row[0])

    def por_username(self, username: str) -> Optional[Usuario]:
        rows = self._db.fetch_all(
            "SELECT id, username, password FROM usuarios WHERE username = ?",
            (username,),
        )
        if not rows:
            return None
        r = rows[0]
        return Usuario(id=int(r[0]), username=str(r[1]), password=str(r[2]))

