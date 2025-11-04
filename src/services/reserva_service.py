from __future__ import annotations

from typing import List, Optional, Literal

from entities.reserva import Reserva
from repositories.reserva_repository import ReservaRepository
from repositories.terreno_repository import TerrenoRepository
from repositories.edificacion_repository import EdificacionRepository

Estado = Literal["ACTIVA", "CANCELADA", "CONFIRMADA"]


class ReservaService:
    """Reglas de negocio para Reservas."""

    def __init__(self) -> None:
        self.repo = ReservaRepository()
        self.trepo = TerrenoRepository()
        self.erepo = EdificacionRepository()

    def _validate(self, r: Reserva) -> None:
        if r.tipo_propiedad == "TERRENO":
            if not self.trepo.find_by_id(r.propiedad_id):
                raise ValueError(f"Terreno {r.propiedad_id} inexistente.")
        elif r.tipo_propiedad == "EDIFICACION":
            if not self.erepo.find_by_id(r.propiedad_id):
                raise ValueError(f"Edificación {r.propiedad_id} inexistente.")

    def crear(self, datos: dict) -> int:
        r = Reserva(**datos)
        self._validate(r)
        return self.repo.create(r)

    def listar(self) -> List[Reserva]:
        return self.repo.find_all()

    def obtener(self, rid: int) -> Optional[Reserva]:
        return self.repo.find_by_id(rid)

    def actualizar(self, rid: int, datos: dict) -> None:
        r = self.repo.find_by_id(rid)
        if not r:
            raise ValueError("Reserva no encontrada.")
        for k, v in (datos or {}).items():
            setattr(r, k, v)
        self._validate(r)
        self.repo.update(r)

    def cancelar(self, rid: int) -> None:
        r = self.repo.find_by_id(rid)
        if not r:
            raise ValueError("Reserva no encontrada.")
        r.estado = "CANCELADA"
        self.repo.update(r)

    def confirmar(self, rid: int) -> None:
        r = self.repo.find_by_id(rid)
        if not r:
            raise ValueError("Reserva no encontrada.")
        r.estado = "CONFIRMADA"
        self.repo.update(r)

    def eliminar(self, rid: int) -> None:
        self.repo.delete(rid)

