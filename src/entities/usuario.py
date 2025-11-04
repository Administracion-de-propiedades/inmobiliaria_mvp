from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """
    Representa a un usuario del sistema.
    Puede ser un administrador, vendedor o encargado de operaciones.
    """

    id: Optional[int] = field(default=None)
    username: str = field(default="")
    password_hash: str = field(default="")
    rol: str = field(default="USER")  # USER, ADMIN, etc.
    activo: bool = field(default=True)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.username:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if len(self.username) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
        if not self.password_hash:
            raise ValueError("El password_hash no puede estar vacío.")

