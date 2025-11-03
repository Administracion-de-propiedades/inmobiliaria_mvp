from __future__ import annotations

from typing import Protocol


class AuthBackend(Protocol):
    """Optional protocol for future authentication backends."""

    def authenticate(self, username: str, password: str) -> bool:  # pragma: no cover - protocol
        ...


class AuthService:
    """Servicio de autenticación.

    MVP: credenciales fijas (admin / 1234). Más adelante, integrar con
    repositorios y hashing de contraseñas.
    """

    def authenticate(self, username: str, password: str) -> bool:
        """Valida credenciales del usuario.

        Args:
            username: Usuario ingresado.
            password: Contraseña ingresada.

        Returns:
            True si las credenciales son correctas; False en caso contrario.
        """
        return username == "admin" and password == "1234"

