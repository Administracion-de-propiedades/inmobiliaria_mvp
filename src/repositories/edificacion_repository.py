from __future__ import annotations

from typing import Iterable, List, Optional

from core.database import Database
from entities.edificacion import Edificacion


class EdificacionRepository:
    """Repositorio de Edificacion con manejo de vínculos N:M a Terrenos."""

    def __init__(self) -> None:
        self.db = Database()

    # ---------- Mappers ----------
    @staticmethod
    def _row_to_entity(row: dict | None, terrenos_ids: Optional[List[int]] = None) -> Optional[Edificacion]:
        if not row:
            return None
        return Edificacion(
            id=row.get("id"),
            nombre=row.get("nombre"),
            tipo=row.get("tipo") or "CASA",
            superficie_cubierta=row.get("superficie_cubierta"),
            ambientes=row.get("ambientes"),
            habitaciones=row.get("habitaciones"),
            banios=row.get("banios"),
            cochera=bool(row.get("cochera")),
            patio=bool(row.get("patio")),
            pileta=bool(row.get("pileta")),
            estado=row.get("estado") or "DISPONIBLE",
            observaciones=row.get("observaciones"),
            created_at=row.get("created_at"),
            terrenos_ids=terrenos_ids or [],
        )

    @staticmethod
    def _rows_to_entities(rows: Iterable[dict]) -> List[Edificacion]:
        return [e for e in (EdificacionRepository._row_to_entity(r, []) for r in rows) if e is not None]

    # ---------- Helpers N:M ----------
    def _get_terrenos_ids(self, edificacion_id: int) -> List[int]:
        sql = "SELECT terreno_id FROM edificacion_terreno WHERE edificacion_id = ? ORDER BY terreno_id"
        rows = self.db.fetch_all(sql, (edificacion_id,))
        return [int(r["terreno_id"]) for r in rows]

    def _replace_terrenos_links(self, edificacion_id: int, terrenos_ids: List[int]) -> None:
        # Reemplaza el set completo de vínculos en una transacción
        # (delete faltantes + insert nuevos)
        existing = set(self._get_terrenos_ids(edificacion_id))
        newset = set(int(t) for t in (terrenos_ids or []))

        to_delete = existing - newset
        to_insert = newset - existing

        for tid in to_delete:
            self.db.execute(
                "DELETE FROM edificacion_terreno WHERE edificacion_id = ? AND terreno_id = ?",
                (edificacion_id, tid),
            )
        for tid in to_insert:
            self.db.execute(
                "INSERT OR IGNORE INTO edificacion_terreno (edificacion_id, terreno_id) VALUES (?, ?)",
                (edificacion_id, tid),
            )

    # ---------- CRUD ----------
    def create(self, e: Edificacion) -> int:
        sql = """
        INSERT INTO edificaciones
        (nombre, tipo, superficie_cubierta, ambientes, habitaciones, banios,
         cochera, patio, pileta, estado, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            e.nombre,
            e.tipo,
            e.superficie_cubierta,
            e.ambientes,
            e.habitaciones,
            e.banios,
            int(bool(e.cochera)),
            int(bool(e.patio)),
            int(bool(e.pileta)),
            e.estado,
            e.observaciones,
        )
        self.db.execute(sql, params)
        row = self.db.fetch_one("SELECT last_insert_rowid() AS id")
        eid = int(row["id"]) if row else 0

        if eid and e.terrenos_ids:
            self._replace_terrenos_links(eid, e.terrenos_ids)
        return eid

    def find_by_id(self, edificacion_id: int) -> Optional[Edificacion]:
        row = self.db.fetch_one("SELECT * FROM edificaciones WHERE id = ?", (edificacion_id,))
        if not row:
            return None
        tids = self._get_terrenos_ids(edificacion_id)
        return self._row_to_entity(row, tids)

    def find_all(self) -> List[Edificacion]:
        rows = self.db.fetch_all("SELECT * FROM edificaciones ORDER BY id")
        result: List[Edificacion] = []
        for r in rows:
            e = self._row_to_entity(r, self._get_terrenos_ids(int(r["id"])))
            if e:
                result.append(e)
        return result

    def list_disponibles(self) -> List[Edificacion]:
        rows = self.db.fetch_all("SELECT * FROM edificaciones WHERE estado = 'DISPONIBLE' ORDER BY id")
        result: List[Edificacion] = []
        for r in rows:
            e = self._row_to_entity(r, self._get_terrenos_ids(int(r["id"])))
            if e:
                result.append(e)
        return result

    def update(self, e: Edificacion) -> None:
        if not e.id:
            raise ValueError("La edificación debe tener 'id' para actualizar.")
        sql = """
        UPDATE edificaciones
        SET nombre = ?, tipo = ?, superficie_cubierta = ?, ambientes = ?, habitaciones = ?, banios = ?,
            cochera = ?, patio = ?, pileta = ?, estado = ?, observaciones = ?
        WHERE id = ?
        """
        params = (
            e.nombre,
            e.tipo,
            e.superficie_cubierta,
            e.ambientes,
            e.habitaciones,
            e.banios,
            int(bool(e.cochera)),
            int(bool(e.patio)),
            int(bool(e.pileta)),
            e.estado,
            e.observaciones,
            e.id,
        )
        self.db.execute(sql, params)
        self._replace_terrenos_links(e.id, e.terrenos_ids or [])

    def delete(self, edificacion_id: int) -> None:
        # ON DELETE CASCADE en la FK limpia vínculos; igual borramos explícito por claridad
        self.db.execute("DELETE FROM edificacion_terreno WHERE edificacion_id = ?", (edificacion_id,))
        self.db.execute("DELETE FROM edificaciones WHERE id = ?", (edificacion_id,))

    # ---------- Consultas útiles ----------
    def list_by_terreno(self, terreno_id: int) -> List[Edificacion]:
        sql = """
        SELECT e.*
        FROM edificaciones e
        JOIN edificacion_terreno et ON et.edificacion_id = e.id
        WHERE et.terreno_id = ?
        ORDER BY e.id
        """
        rows = self.db.fetch_all(sql, (terreno_id,))
        result: List[Edificacion] = []
        for r in rows:
            e = self._row_to_entity(r, self._get_terrenos_ids(int(r["id"])))
            if e:
                result.append(e)
        return result

