from __future__ import annotations

from typing import List, Optional, Iterable, Literal

from entities.loteo import Loteo
from repositories.loteo_repository import LoteoRepository
from repositories.terreno_repository import TerrenoRepository

Estado = Literal["ACTIVO", "PAUSADO", "CERRADO"]


class LoteoService:
    def __init__(self, lrepo: Optional[LoteoRepository] = None, trepo: Optional[TerrenoRepository] = None) -> None:
        self.lrepo = lrepo or LoteoRepository()
        self.trepo = trepo or TerrenoRepository()

    def _validate(self, l: Loteo) -> None:
        if l.estado not in ("ACTIVO","PAUSADO","CERRADO"):
            raise ValueError("Estado de loteo inválido.")
        # validar existencia de terrenos elegidos
        for tid in l.terrenos_ids or []:
            if not self.trepo.find_by_id(int(tid)):
                raise ValueError(f"Terreno inexistente (id={tid}).")

    def crear(self, datos: dict) -> int:
        l = Loteo(**datos)
        self._validate(l)
        return self.lrepo.create(l)

    def actualizar(self, loteo_id: int, datos: dict) -> None:
        actual = self.lrepo.find_by_id(loteo_id)
        if not actual:
            raise ValueError("Loteo no encontrado.")
        for k, v in (datos or {}).items():
            setattr(actual, k, v)
        self._validate(actual)
        self.lrepo.update(actual)

    def obtener(self, loteo_id: int) -> Optional[Loteo]:
        return self.lrepo.find_by_id(loteo_id)

    def listar(self) -> List[Loteo]:
        return self.lrepo.find_all()

    def eliminar(self, loteo_id: int) -> None:
        # regla: permitir borrar, desasignando primero todos los terrenos
        self.lrepo.delete(loteo_id)

    # vínculos
    def reemplazar_terrenos(self, loteo_id: int, nuevos_ids: Iterable[int]) -> None:
        # valida y delega
        for tid in (nuevos_ids or []):
            if not self.trepo.find_by_id(int(tid)):
                raise ValueError(f"Terreno inexistente (id={tid}).")
        self.lrepo.reemplazar_terrenos(loteo_id, list(dict.fromkeys(int(t) for t in (nuevos_ids or []))))

