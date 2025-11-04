from __future__ import annotations

import sys
from pathlib import Path


# Ensure `src` is on the import path when running from project root
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from config.settings import get_settings  # type: ignore  # noqa: E402


def main() -> None:
    settings = get_settings()

    # Lazy import to avoid optional dependency issues in environments
    from core.database import Database  # type: ignore  # noqa: E402

    try:
        db = Database()
        db.connect()
        print(f"Conectado a {db.settings.db_engine} -> {db.settings.db_name}")
        # Basic DDL/DML test for sqlite
        if settings.db_engine == "sqlite":
            db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
            db.execute("INSERT INTO test (name) VALUES (?)", ("demo",))
            rows = db.fetch_all("SELECT * FROM test")
            print("fetch_all:", rows)
        db.close()
    except Exception as exc:  # pragma: no cover - diagnostic script
        print(f"Connection failed: {exc}")
        sys.exit(1)

    # --- Entidad Usuario quick test ---
    from entities.usuario import Usuario  # type: ignore  # noqa: E402

    print("\n=== TEST USUARIO ===")
    user = Usuario(username="admin", password_hash="123456hash", rol="ADMIN")
    print(user)


if __name__ == "__main__":
    main()

from repositories.usuario_repository import UsuarioRepository
from entities.usuario import Usuario
import uuid

print("\n=== TEST USUARIO REPOSITORY ===")
repo = UsuarioRepository()

# Crear usuario demo con sufijo único para evitar colisiones
uname = f"demo_user_{uuid.uuid4().hex[:6]}"
user = Usuario(username=uname, password_hash="hashdemo", rol="ADMIN")
user_id = repo.create(user)
print("Usuario creado con ID:", user_id)

# Buscar usuario
found = repo.find_by_id(user_id)
print("Usuario encontrado:", found)

# Actualizar usuario
if found:
    # Evitar colisiones de UNIQUE(username) en re-ejecuciones
    found.username = f"demo_updated_{user_id}"
    repo.update(found)
    print("Usuario actualizado:", repo.find_by_id(user_id))

# Listar todos
print("Usuarios activos:", repo.find_all())

# Eliminar (baja lógica)
repo.delete(user_id)
print("Usuarios activos luego de eliminar:", repo.find_all())

# --- AuthService quick test ---
from services.auth_service import AuthService  # type: ignore  # noqa: E402
print("\n=== TEST AUTH ===")
svc = AuthService()
print("Login admin/admin:", bool(svc.authenticate("admin", "admin")))
print("Login admin/wrong:", bool(svc.authenticate("admin", "wrong")))
