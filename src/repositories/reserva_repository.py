from __future__ import annotations

from typing import List, Optional

from core.database import Database
from entities.reserva import Reserva


class ReservaRepository:
    """Repositorio CRUD para reservas polimórficas (Terreno o Edificación)."""

    def __init__(self) -> None:
        self.db = Database()

    def _row_to_entity(self, row: dict | None) -> Optional[Reserva]:
        if not row:
            return None
        return Reserva(**row)

    def create(self, r: Reserva) -> int:
        sql = """
        INSERT INTO reservas (tipo_propiedad, propiedad_id, cliente, fecha_reserva, monto_reserva, estado, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(sql, (
            r.tipo_propiedad, r.propiedad_id, r.cliente,
            r.fecha_reserva, r.monto_reserva, r.estado, r.observaciones
        ))
        row = self.db.fetch_one("SELECT last_insert_rowid() AS id")
        return int(row["id"]) if row else 0

    def find_by_id(self, rid: int) -> Optional[Reserva]:
        row = self.db.fetch_one("SELECT * FROM reservas WHERE id = ?", (rid,))
        return self._row_to_entity(row)

    def find_all(self) -> List[Reserva]:
        rows = self.db.fetch_all("SELECT * FROM reservas ORDER BY id DESC")
        return [self._row_to_entity(r) for r in rows if r]

    def update(self, r: Reserva) -> None:
        if not r.id:
            raise ValueError("Reserva sin id.")
        sql = """
        UPDATE reservas
        SET tipo_propiedad=?, propiedad_id=?, cliente=?, fecha_reserva=?, monto_reserva=?, estado=?, observaciones=?
        WHERE id=?
        """
        self.db.execute(sql, (
            r.tipo_propiedad, r.propiedad_id, r.cliente,
            r.fecha_reserva, r.monto_reserva, r.estado, r.observaciones, r.id
        ))

    def delete(self, rid: int) -> None:
        self.db.execute("DELETE FROM reservas WHERE id=?", (rid,))

