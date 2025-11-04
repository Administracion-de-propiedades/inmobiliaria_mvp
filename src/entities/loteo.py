from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal, List

EstadoLoteo = Literal["ACTIVO", "PAUSADO", "CERRADO"]


@dataclass
class Loteo:
    id: Optional[int] = field(default=None)
    nombre: str = field(default="")
    ubicacion: Optional[str] = field(default=None)
    municipio: Optional[str] = field(default=None)
    provincia: Optional[str] = field(default=None)
    fecha_inicio: Optional[str] = field(default=None)  # yyyy-mm-dd
    fecha_fin: Optional[str] = field(default=None)
    estado: EstadoLoteo = field(default="ACTIVO")
    observaciones: Optional[str] = field(default=None)
    # decorativo para UI: ids de terrenos asignados
    terrenos_ids: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise ValueError("El nombre de loteo es obligatorio (>=3).")
        if self.estado not in ("ACTIVO", "PAUSADO", "CERRADO"):
            raise ValueError("Estado de loteo inválido.")

