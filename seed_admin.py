from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from services.auth_service import AuthService  # type: ignore  # noqa: E402


if __name__ == "__main__":
    svc = AuthService()
    user_id = svc.ensure_admin(username="admin", password="admin", rol="ADMIN")
    if user_id:
        print(f"Admin creado con id={user_id}")
    else:
        print("Admin ya existía.")
