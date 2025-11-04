from __future__ import annotations

from typing import List, Optional, Iterable, Literal

from entities.edificacion import Edificacion, TipoEdificacion, EstadoEdificacion
from repositories.edificacion_repository import EdificacionRepository
from repositories.terreno_repository import TerrenoRepository

Estado = Literal["DISPONIBLE", "RESERVADO", "VENDIDO"]


class EdificacionService:
    """Capa de negocio para Edificacion: validaciones, vínculos y estados."""

    def __init__(
        self,
        erepo: Optional[EdificacionRepository] = None,
        trepo: Optional[TerrenoRepository] = None,
    ) -> None:
        self.erepo = erepo or EdificacionRepository()
        self.trepo = trepo or TerrenoRepository()

    # ---------- Validaciones ----------
    def _validate_core(self, e: Edificacion) -> None:
        if e.tipo not in ("CASA", "DUPLEX", "DEPARTAMENTO", "LOCAL", "GALPON"):
            raise ValueError("Tipo de edificación inválido.")
        if e.estado not in ("DISPONIBLE", "RESERVADO", "VENDIDO"):
            raise ValueError("Estado de edificación inválido.")
        if e.superficie_cubierta is not None and e.superficie_cubierta <= 0:
            raise ValueError("superficie_cubierta debe ser > 0 si se informa.")
        for val in (e.ambientes, e.habitaciones, e.banios):
            if val is not None and val < 0:
                raise ValueError("Los contadores no pueden ser negativos.")

    def _validate_terrenos_exist(self, terrenos_ids: Iterable[int]) -> None:
        if terrenos_ids is None:
            return
        for tid in terrenos_ids:
            if not self.trepo.find_by_id(int(tid)):
                raise ValueError(f"Terreno inexistente (id={tid}).")

    # ---------- Reglas de estado ----------
    def _can_transition(self, actual: Estado, nuevo: Estado) -> bool:
        if actual == "DISPONIBLE":
            return nuevo in ("DISPONIBLE", "RESERVADO", "VENDIDO")
        if actual == "RESERVADO":
            return nuevo in ("RESERVADO", "DISPONIBLE", "VENDIDO")
        if actual == "VENDIDO":
            # No se puede revertir venta
            return nuevo == "VENDIDO"
        return False

    # ---------- API de creación/lectura ----------
    def crear(self, datos: dict) -> int:
        """
        Crea una edificación.
        Reglas:
         - Si estado = VENDIDO, debe tener al menos 1 terreno vinculado.
         - Validar existencia de los terrenos.
        """
        e = Edificacion(**datos)
        self._validate_core(e)
        self._validate_terrenos_exist(e.terrenos_ids)
        if e.estado == "VENDIDO" and not e.terrenos_ids:
            raise ValueError("No se puede vender una edificación sin terrenos asociados.")
        return self.erepo.create(e)

    def obtener(self, eid: int) -> Optional[Edificacion]:
        return self.erepo.find_by_id(eid)

    def listar(self) -> List[Edificacion]:
        return self.erepo.find_all()

    def listar_disponibles(self) -> List[Edificacion]:
        return self.erepo.list_disponibles()

    # ---------- API de actualización ----------
    def actualizar(self, eid: int, datos: dict) -> None:
        actual = self.erepo.find_by_id(eid)
        if not actual:
            raise ValueError("Edificación no encontrada.")
        # Merge
        for k, v in (datos or {}).items():
            setattr(actual, k, v)
        self._validate_core(actual)
        self._validate_terrenos_exist(actual.terrenos_ids)
        if actual.estado == "VENDIDO" and not actual.terrenos_ids:
            raise ValueError("Una edificación VENDIDA debe mantener al menos un terreno vinculado.")
        self.erepo.update(actual)

    # ---------- Vínculos N:M ----------
    def reemplazar_terrenos(self, eid: int, nuevos_terrenos_ids: Iterable[int]) -> None:
        e = self.erepo.find_by_id(eid)
        if not e:
            raise ValueError("Edificación no encontrada.")
        nuevos = list(dict.fromkeys(int(t) for t in (nuevos_terrenos_ids or [])))  # sin duplicados
        self._validate_terrenos_exist(nuevos)
        if e.estado == "VENDIDO" and not nuevos:
            raise ValueError("No se puede dejar sin terrenos una edificación VENDIDA.")
        e.terrenos_ids = nuevos
        self.erepo.update(e)

    def agregar_terreno(self, eid: int, terreno_id: int) -> None:
        e = self.erepo.find_by_id(eid)
        if not e:
            raise ValueError("Edificación no encontrada.")
        self._validate_terrenos_exist([terreno_id])
        if terreno_id not in e.terrenos_ids:
            e.terrenos_ids.append(int(terreno_id))
            self.erepo.update(e)

    def quitar_terreno(self, eid: int, terreno_id: int) -> None:
        e = self.erepo.find_by_id(eid)
        if not e:
            raise ValueError("Edificación no encontrada.")
        if terreno_id in e.terrenos_ids:
            if e.estado == "VENDIDO" and len(e.terrenos_ids) <= 1:
                raise ValueError("No se puede quitar el último terreno de una edificación VENDIDA.")
            e.terrenos_ids = [t for t in e.terrenos_ids if t != int(terreno_id)]
            self.erepo.update(e)

    # ---------- Estado ----------
    def cambiar_estado(self, eid: int, nuevo_estado: Estado) -> None:
        e = self.erepo.find_by_id(eid)
        if not e:
            raise ValueError("Edificación no encontrada.")
        if not self._can_transition(e.estado, nuevo_estado):
            raise ValueError(f"Transición de estado inválida: {e.estado} → {nuevo_estado}")
        if nuevo_estado == "VENDIDO" and not e.terrenos_ids:
            raise ValueError("Para marcar como VENDIDO debe haber al menos un terreno vinculado.")
        e.estado = nuevo_estado
        self.erepo.update(e)

    # ---------- Eliminación ----------
    def eliminar(self, eid: int) -> None:
        e = self.erepo.find_by_id(eid)
        if not e:
            return
        if e.estado == "VENDIDO":
            raise ValueError("No se puede eliminar una edificación VENDIDA.")
        self.erepo.delete(eid)

