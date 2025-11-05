from __future__ import annotations

from typing import Iterable, List, Optional

from core.database import Database
from entities.terreno import Terreno


class TerrenoRepository:
    """Repositorio para la entidad Terreno."""

    def __init__(self) -> None:
        self.db = Database()

    # ---- Mappers ----
    @staticmethod
    def _row_to_entity(row: dict | None) -> Optional[Terreno]:
        if not row:
            return None
        return Terreno(
            id=row.get("id"),
            manzana=row.get("manzana") or "",
            numero_lote=row.get("numero_lote") or "",
            superficie=float(row.get("superficie") or 0),
            ubicacion=row.get("ubicacion"),
            nomenclatura=row.get("nomenclatura"),
            estado=row.get("estado") or "DISPONIBLE",
            observaciones=row.get("observaciones"),
            created_at=row.get("created_at"),
        )

    @staticmethod
    def _rows_to_entities(rows: Iterable[dict]) -> List[Terreno]:
        return [e for e in (TerrenoRepository._row_to_entity(r) for r in rows) if e is not None]

    # ---- CRUD ----
    def create(self, t: Terreno) -> int:
        """
        Inserta un Terreno y retorna su ID (SQLite).
        Para PostgreSQL, se reemplazará por RETURNING id.
        """
        sql = (
            """
        INSERT INTO terrenos (manzana, numero_lote, superficie, ubicacion,
                              nomenclatura, estado, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        )
        params = (
            t.manzana,
            t.numero_lote,
            t.superficie,
            t.ubicacion,
            t.nomenclatura,
            t.estado,
            t.observaciones,
        )
        self.db.execute(sql, params)
        row = self.db.fetch_one("SELECT last_insert_rowid() AS id")
        return int(row["id"]) if row else 0

    def find_by_id(self, terreno_id: int) -> Optional[Terreno]:
        row = self.db.fetch_one("SELECT * FROM terrenos WHERE id = ?", (terreno_id,))
        return self._row_to_entity(row)

    def find_all(self) -> List[Terreno]:
        rows = self.db.fetch_all("SELECT * FROM terrenos ORDER BY id")
        return self._rows_to_entities(rows)

    def list_disponibles(self) -> List[Terreno]:
        rows = self.db.fetch_all("SELECT * FROM terrenos WHERE estado = 'DISPONIBLE' ORDER BY id")
        return self._rows_to_entities(rows)

    def update(self, t: Terreno) -> None:
        if not t.id:
            raise ValueError("El Terreno debe tener 'id' para actualizar.")
        sql = (
            """
        UPDATE terrenos
        SET manzana = ?, numero_lote = ?, superficie = ?,
            ubicacion = ?, nomenclatura = ?, estado = ?, observaciones = ?
        WHERE id = ?
        """
        )
        params = (
            t.manzana,
            t.numero_lote,
            t.superficie,
            t.ubicacion,
            t.nomenclatura,
            t.estado,
            t.observaciones,
            t.id,
        )
        self.db.execute(sql, params)

    def delete(self, terreno_id: int) -> None:
        """Eliminación física (simple). Más adelante podemos implementar baja lógica."""
        self.db.execute("DELETE FROM terrenos WHERE id = ?", (terreno_id,))
