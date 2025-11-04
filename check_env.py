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

# --- Verificación tabla 'terrenos' creada ---
from core.database import Database  # type: ignore  # noqa: E402
db = Database()
try:
    if get_settings().db_engine == "sqlite":  # type: ignore  # noqa: F821
        rows = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table' AND name='terrenos'")
        print("Tabla 'terrenos' creada:", bool(rows))
    else:
        # Opcional: verificación simple para PostgreSQL
        rows = db.fetch_all("SELECT to_regclass('public.terrenos')")
        print("Tabla 'terrenos' creada:", bool(rows and rows[0][0]))
finally:
    db.close()

from entities.terreno import Terreno

print("\n=== TEST ENTIDAD TERRENO ===")
try:
    t = Terreno(manzana="A", numero_lote="12", superficie=250.0, ubicacion="Barrio Centro")
    print("OK:", t.display_name(), t.superficie, t.estado)
except Exception as e:
    print("Terreno inválido:", e)

from repositories.terreno_repository import TerrenoRepository
from entities.terreno import Terreno

print("\n=== TEST TERRENO REPOSITORY ===")
trepo = TerrenoRepository()

# Crear
ter = Terreno(manzana="B", numero_lote="21", superficie=300.0, ubicacion="Barrio Norte")
tid = trepo.create(ter)
print("Creado ID:", tid)

# Leer por ID
t_db = trepo.find_by_id(tid)
print("Leído:", t_db)

# Listar todos
print("Todos:", trepo.find_all())

# Listar disponibles
print("Disponibles:", trepo.list_disponibles())

# Actualizar
if t_db:
    t_db.superficie = 320.5
    t_db.estado = "RESERVADO"
    trepo.update(t_db)
    print("Actualizado:", trepo.find_by_id(tid))

# Borrar
trepo.delete(tid)
print("Existe tras borrar:", trepo.find_by_id(tid))

from services.terreno_service import TerrenoService

print("\n=== TEST TERRENO SERVICE ===")
svc = TerrenoService()

# Crear OK
tid = svc.crear({
    "manzana": "C",
    "numero_lote": "5",
    "superficie": 200.0,
    "ubicacion": "Barrio Sur"
})
print("Creado ID:", tid)

# Duplicado (espera error)
try:
    svc.crear({"manzana": "C", "numero_lote": "5", "superficie": 180.0})
except Exception as e:
    print("Duplicado OK:", e)

# Cambiar estado
svc.cambiar_estado(tid, "RESERVADO")
print("Estado tras reservar:", svc.obtener(tid).estado)

# Intentar reservar de nuevo (error)
try:
    svc.cambiar_estado(tid, "RESERVADO")
except Exception as e:
    print("Regla reserva OK:", e)

# Vender
svc.cambiar_estado(tid, "VENDIDO")
print("Estado tras vender:", svc.obtener(tid).estado)

# Intentar revertir venta (error)
try:
    svc.cambiar_estado(tid, "DISPONIBLE")
except Exception as e:
    print("No revertir venta OK:", e)

# Actualizar datos
svc.actualizar(tid, {"superficie": 210.5, "nomenclatura": "NC-123"})
print("Superficie:", svc.obtener(tid).superficie)
