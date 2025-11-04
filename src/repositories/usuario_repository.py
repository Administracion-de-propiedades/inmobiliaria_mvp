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
                password_hash TEXT NOT NULL,
                rol TEXT DEFAULT 'USER',
                activo BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    def crear(self, usuario: Usuario) -> int:
        self._db.execute(
            "INSERT INTO usuarios (username, password_hash, rol, activo) VALUES (?, ?, ?, ?)",
            (usuario.username, usuario.password_hash, usuario.rol, 1 if usuario.activo else 0),
        )
        row = self._db.fetch_one("SELECT last_insert_rowid() as id")
        return int(row["id"]) if row else 0

    def por_username(self, username: str) -> Optional[Usuario]:
        rows = self._db.fetch_all(
            "SELECT id, username, password_hash, rol, activo, created_at FROM usuarios WHERE username = ?",
            (username,),
        )
        if not rows:
            return None
        r = rows[0]
        return Usuario(
            id=int(r["id"]),
            username=str(r["username"]),
            password_hash=str(r["password_hash"]),
            rol=str(r.get("rol", "USER")),
            activo=bool(r.get("activo", 1)),
            created_at=r.get("created_at"),
        )

