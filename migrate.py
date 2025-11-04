from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure `src` is on path when running from project root
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from config.settings import configure_logging  # noqa: E402
from core.migrations import MigrationManager  # noqa: E402


def main() -> None:
    configure_logging()
    mm = MigrationManager()
    base_path = os.path.join(os.path.dirname(__file__), "src", "migrations")

    # Leer todos los archivos SQL ordenados por nombre
    files = sorted(f for f in os.listdir(base_path) if f.endswith(".sql"))
    for f in files:
        with open(os.path.join(base_path, f), "r", encoding="utf-8") as sql_file:
            sql = sql_file.read()
            mm.apply_migration(f, sql)


if __name__ == "__main__":
    main()

