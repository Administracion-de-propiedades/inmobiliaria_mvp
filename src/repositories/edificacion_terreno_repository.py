from __future__ import annotations

from typing import Iterable, List

from core.database import Database


class EdificacionTerrenoRepository:
    """
    Repositorio para la tabla puente 'edificacion_terreno' (N:M).
    Provee operaciones atómicas de vinculación, desvinculación
    y consultas cruzadas por cada lado.
    """

    def __init__(self) -> None:
        self.db = Database()

    # -------- Consultas --------
    def terrenos_ids_de_edificacion(self, edificacion_id: int) -> List[int]:
        rows = self.db.fetch_all(
            "SELECT terreno_id FROM edificacion_terreno WHERE edificacion_id = ? ORDER BY terreno_id",
            (edificacion_id,),
        )
        return [int(r["terreno_id"]) for r in rows]

    def edificaciones_ids_de_terreno(self, terreno_id: int) -> List[int]:
        rows = self.db.fetch_all(
            "SELECT edificacion_id FROM edificacion_terreno WHERE terreno_id = ? ORDER BY edificacion_id",
            (terreno_id,),
        )
        return [int(r["edificacion_id"]) for r in rows]

    # -------- Mutaciones --------
    def vincular(self, edificacion_id: int, terreno_id: int) -> None:
        """Crea el vínculo si no existía (idempotente)."""
        self.db.execute(
            "INSERT OR IGNORE INTO edificacion_terreno (edificacion_id, terreno_id) VALUES (?, ?)",
            (edificacion_id, terreno_id),
        )

    def desvincular(self, edificacion_id: int, terreno_id: int) -> None:
        self.db.execute(
            "DELETE FROM edificacion_terreno WHERE edificacion_id = ? AND terreno_id = ?",
            (edificacion_id, terreno_id),
        )

    def reemplazar_terrenos(self, edificacion_id: int, nuevos_terrenos_ids: Iterable[int]) -> None:
        """
        Reemplaza el conjunto completo de vínculos para una edificación.
        Elimina los faltantes e inserta los nuevos (idempotente).
        """
        actuales = set(self.terrenos_ids_de_edificacion(edificacion_id))
        nuevos = set(int(t) for t in (nuevos_terrenos_ids or []))

        a_borrar = actuales - nuevos
        a_insertar = nuevos - actuales

        for tid in a_borrar:
            self.desvincular(edificacion_id, tid)
        for tid in a_insertar:
            self.vincular(edificacion_id, tid)

    def reemplazar_edificaciones(self, terreno_id: int, nuevas_edificaciones_ids: Iterable[int]) -> None:
        """Reemplaza el conjunto completo de vínculos para un terreno."""
        actuales = set(self.edificaciones_ids_de_terreno(terreno_id))
        nuevos = set(int(e) for e in (nuevas_edificaciones_ids or []))

        a_borrar = actuales - nuevos
        a_insertar = nuevos - actuales

        for eid in a_borrar:
            self.db.execute(
                "DELETE FROM edificacion_terreno WHERE edificacion_id = ? AND terreno_id = ?",
                (eid, terreno_id),
            )
        for eid in a_insertar:
            self.vincular(eid, terreno_id)

