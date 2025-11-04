from __future__ import annotations

from typing import List, Optional, Iterable

from core.database import Database
from entities.loteo import Loteo


class LoteoRepository:
    """CRUD de Loteo + asignación de Terrenos (vía campo loteo_id en terrenos)."""

    def __init__(self) -> None:
        self.db = Database()

    # --- mappers
    @staticmethod
    def _row_to_entity(row: dict | None, terrenos_ids: Optional[List[int]] = None) -> Optional[Loteo]:
        if not row:
            return None
        return Loteo(
            id=row.get("id"),
            nombre=row.get("nombre") or "",
            ubicacion=row.get("ubicacion"),
            municipio=row.get("municipio"),
            provincia=row.get("provincia"),
            fecha_inicio=row.get("fecha_inicio"),
            fecha_fin=row.get("fecha_fin"),
            estado=row.get("estado") or "ACTIVO",
            observaciones=row.get("observaciones"),
            terrenos_ids=terrenos_ids or [],
        )

    def _terrenos_ids_de_loteo(self, loteo_id: int) -> List[int]:
        rows = self.db.fetch_all("SELECT id FROM terrenos WHERE loteo_id = ? ORDER BY id", (loteo_id,))
        return [int(r["id"]) for r in rows]

    # --- CRUD
    def create(self, l: Loteo) -> int:
        sql = """
        INSERT INTO loteos (nombre, ubicacion, municipio, provincia, fecha_inicio, fecha_fin, estado, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(sql, (l.nombre, l.ubicacion, l.municipio, l.provincia, l.fecha_inicio, l.fecha_fin, l.estado, l.observaciones))
        row = self.db.fetch_one("SELECT last_insert_rowid() AS id")
        lid = int(row["id"]) if row else 0
        if lid and l.terrenos_ids:
            self.reemplazar_terrenos(lid, l.terrenos_ids)
        return lid

    def find_by_id(self, loteo_id: int) -> Optional[Loteo]:
        row = self.db.fetch_one("SELECT * FROM loteos WHERE id = ?", (loteo_id,))
        if not row:
            return None
        tids = self._terrenos_ids_de_loteo(loteo_id)
        return self._row_to_entity(row, tids)

    def find_all(self) -> List[Loteo]:
        rows = self.db.fetch_all("SELECT * FROM loteos ORDER BY id")
        result: List[Loteo] = []
        for r in rows:
            lid = int(r["id"])
            result.append(self._row_to_entity(r, self._terrenos_ids_de_loteo(lid)))
        return result

    def update(self, l: Loteo) -> None:
        if not l.id:
            raise ValueError("Loteo sin id.")
        sql = """
        UPDATE loteos
        SET nombre=?, ubicacion=?, municipio=?, provincia=?, fecha_inicio=?, fecha_fin=?, estado=?, observaciones=?
        WHERE id=?
        """
        self.db.execute(sql, (l.nombre, l.ubicacion, l.municipio, l.provincia, l.fecha_inicio, l.fecha_fin, l.estado, l.observaciones, l.id))
        # vínculos
        self.reemplazar_terrenos(l.id, l.terrenos_ids or [])

    def delete(self, loteo_id: int) -> None:
        # desasignar terrenos del loteo antes de borrar
        self.db.execute("UPDATE terrenos SET loteo_id=NULL WHERE loteo_id = ?", (loteo_id,))
        self.db.execute("DELETE FROM loteos WHERE id = ?", (loteo_id,))

    # --- vínculos (vía campo loteo_id en terrenos)
    def reemplazar_terrenos(self, loteo_id: int, nuevos_ids: Iterable[int]) -> None:
        actuales = set(self._terrenos_ids_de_loteo(loteo_id))
        nuevos = set(int(t) for t in (nuevos_ids or []))
        a_quitar = actuales - nuevos
        a_agregar = nuevos - actuales
        if a_quitar:
            self.db.execute(f"UPDATE terrenos SET loteo_id=NULL WHERE loteo_id=? AND id IN ({','.join('?'*len(a_quitar))})", (loteo_id, *a_quitar))
        for tid in a_agregar:
            self.db.execute("UPDATE terrenos SET loteo_id=? WHERE id=?", (loteo_id, tid))

