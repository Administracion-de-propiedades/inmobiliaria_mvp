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
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )

    def crear(self, usuario: Usuario) -> int:
        self._db.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (usuario.username, usuario.password),
        )
        row = self._db.fetch_one("SELECT last_insert_rowid() as id")
        return int(row["id"]) if row else 0

    def por_username(self, username: str) -> Optional[Usuario]:
        rows = self._db.fetch_all(
            "SELECT id, username, password FROM usuarios WHERE username = ?",
            (username,),
        )
        if not rows:
            return None
        r = rows[0]
        return Usuario(id=int(r["id"]), username=str(r["username"]), password=str(r["password"]))

