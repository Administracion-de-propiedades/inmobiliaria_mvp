from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional

TipoEdificacion = Literal["CASA", "DUPLEX", "DEPARTAMENTO", "LOCAL", "GALPON"]
EstadoEdificacion = Literal["DISPONIBLE", "RESERVADO", "VENDIDO"]


@dataclass
class Edificacion:
    """
    Representa una propiedad edificada.
    Se asocia a uno o varios Terrenos vía la tabla puente 'edificacion_terreno'.
    """

    id: Optional[int] = field(default=None)
    nombre: Optional[str] = field(default=None)
    tipo: TipoEdificacion = field(default="CASA")
    superficie_cubierta: Optional[float] = field(default=None)
    ambientes: Optional[int] = field(default=None)
    habitaciones: Optional[int] = field(default=None)
    banios: Optional[int] = field(default=None)  # usar ASCII (banios)
    cochera: bool = field(default=False)
    patio: bool = field(default=False)
    pileta: bool = field(default=False)
    estado: EstadoEdificacion = field(default="DISPONIBLE")
    observaciones: Optional[str] = field(default=None)
    created_at: Optional[datetime] = field(default=None)

    # Relación N:M (no se persiste aquí, es decorativa para repos/servicios)
    terrenos_ids: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.tipo not in ("CASA", "DUPLEX", "DEPARTAMENTO", "LOCAL", "GALPON"):
            raise ValueError("Tipo de edificación inválido.")
        if self.estado not in ("DISPONIBLE", "RESERVADO", "VENDIDO"):
            raise ValueError("Estado de edificación inválido.")
        if self.superficie_cubierta is not None and self.superficie_cubierta <= 0:
            raise ValueError("superficie_cubierta debe ser > 0 si se informa.")
        for val in (self.ambientes, self.habitaciones, self.banios):
            if val is not None and val < 0:
                raise ValueError("Los contadores no pueden ser negativos.")

    def display_name(self) -> str:
        """
        Etiqueta amigable para listados (ej: 'CASA – 120 m²' o solo 'CASA' si no hay superficie).
        """
        base = self.tipo
        if self.superficie_cubierta:
            if float(self.superficie_cubierta).is_integer():
                base += f" – {int(self.superficie_cubierta)} m²"
            else:
                base += f" – {self.superficie_cubierta} m²"
        return base

