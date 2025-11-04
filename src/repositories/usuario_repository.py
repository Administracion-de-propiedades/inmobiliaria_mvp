from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from core.database import Database
from entities.usuario import Usuario


class UsuarioRepository:
    """Repositorio para operaciones CRUD sobre la tabla usuarios."""

    def __init__(self) -> None:
        self.db = Database()

    @staticmethod
    def _row_to_usuario(row: dict) -> Usuario:
        created = row.get("created_at")
        if isinstance(created, str):
            try:
                created_dt = datetime.fromisoformat(created)
            except Exception:
                created_dt = datetime.now()
        elif isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.now()
        return Usuario(
            id=int(row.get("id")) if row.get("id") is not None else None,
            username=str(row.get("username", "")),
            password_hash=str(row.get("password_hash", "")),
            rol=str(row.get("rol", "USER")),
            activo=bool(row.get("activo", 1)),
            created_at=created_dt,
        )

    def create(self, usuario: Usuario) -> int:
        """Inserta un nuevo usuario y retorna su ID."""
        query = (
            """
        INSERT INTO usuarios (username, password_hash, rol, activo)
        VALUES (?, ?, ?, ?)
        """
        )
        params = (usuario.username, usuario.password_hash, usuario.rol, usuario.activo)
        self.db.execute(query, params)
        row = self.db.fetch_one("SELECT last_insert_rowid() AS id")
        return int(row["id"]) if row else 0

    def find_by_id(self, user_id: int) -> Optional[Usuario]:
        """Busca un usuario por ID."""
        row = self.db.fetch_one("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        return self._row_to_usuario(row) if row else None

    def find_by_username(self, username: str) -> Optional[Usuario]:
        """Busca un usuario por nombre de usuario."""
        row = self.db.fetch_one("SELECT * FROM usuarios WHERE username = ?", (username,))
        return self._row_to_usuario(row) if row else None

    def find_all(self) -> List[Usuario]:
        """Devuelve todos los usuarios activos."""
        rows = self.db.fetch_all("SELECT * FROM usuarios WHERE activo = 1 ORDER BY id")
        return [self._row_to_usuario(r) for r in rows]

    def update(self, usuario: Usuario) -> None:
        """Actualiza datos de un usuario existente."""
        query = (
            """
        UPDATE usuarios
        SET username = ?, password_hash = ?, rol = ?, activo = ?
        WHERE id = ?
        """
        )
        params = (usuario.username, usuario.password_hash, usuario.rol, usuario.activo, usuario.id)
        self.db.execute(query, params)

    def delete(self, user_id: int) -> None:
        """Elimina lógicamente (inactiva) un usuario."""
        self.db.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (user_id,))

