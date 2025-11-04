from __future__ import annotations

from typing import Optional

import bcrypt

from entities.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


BCRYPT_PREFIXES = (b"$2a$", b"$2b$", b"$2y$")


class AuthService:
    """Autenticación de usuarios con bcrypt (hash + verify)."""

    def __init__(self, repo: Optional[UsuarioRepository] = None) -> None:
        self.repo = repo or UsuarioRepository()

    # ----------------- Helpers de hash -----------------
    @staticmethod
    def hash_password(plain_password: str, rounds: int = 12) -> str:
        """
        Retorna un hash bcrypt seguro para el password dado.
        rounds=12 es un buen balance CPU/seguridad para desktop.
        """
        if not plain_password:
            raise ValueError("El password no puede ser vacío")
        salt = bcrypt.gensalt(rounds)
        h = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return h.decode("utf-8")

    @staticmethod
    def looks_like_bcrypt(value: str) -> bool:
        """Detecta si el string parece un hash bcrypt válido."""
        try:
            return value.encode("utf-8").startswith(BCRYPT_PREFIXES) and len(value) >= 60
        except Exception:
            return False

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Verifica un password plano contra un hash bcrypt."""
        if not AuthService.looks_like_bcrypt(password_hash):
            # Defensa contra "Invalid salt": si el campo no es hash, falla controlado.
            return False
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
        except ValueError:
            # bcrypt lanza ValueError: Invalid salt si el hash está corrupto
            return False

    # ----------------- API principal -----------------
    def authenticate(self, username: str, password: str) -> Optional[Usuario]:
        """
        Retorna el Usuario si las credenciales son válidas; de lo contrario None.
        """
        user = self.repo.find_by_username(username)
        if not user or not user.activo:
            return None
        if self.verify_password(password, user.password_hash):
            return user
        return None

    def create_user(self, username: str, plain_password: str, rol: str = "USER", activo: bool = True) -> int:
        """Crea usuario con hash seguro."""
        ph = self.hash_password(plain_password)
        u = Usuario(username=username, password_hash=ph, rol=rol, activo=activo)
        return self.repo.create(u)

    # --------- Utilities opcionales ---------
    def ensure_admin(self, username: str = "admin", password: str = "admin", rol: str = "ADMIN") -> int | None:
        """
        Crea un admin por defecto si no existe. No sobreescribe si ya está creado.
        Retorna el ID creado o None si ya existía.
        """
        existing = self.repo.find_by_username(username)
        if existing:
            return None
        return self.create_user(username=username, plain_password=password, rol=rol, activo=True)

