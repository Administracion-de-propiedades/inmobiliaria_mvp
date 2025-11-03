from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Usuario:
    """Entidad de usuario del sistema.

    En futuras iteraciones, las contraseñas deben manejarse con hashing seguro.
    """

    id: Optional[int]
    username: str
    password: str

