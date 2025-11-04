from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal

TipoPropiedad = Literal["TERRENO", "EDIFICACION"]
EstadoReserva = Literal["ACTIVA", "CANCELADA", "CONFIRMADA"]


@dataclass
class Reserva:
    id: Optional[int] = field(default=None)
    tipo_propiedad: TipoPropiedad = field(default="TERRENO")
    propiedad_id: int = field(default=0)
    cliente: str = field(default="")
    fecha_reserva: str = field(default="")
    monto_reserva: float = field(default=0.0)
    estado: EstadoReserva = field(default="ACTIVA")
    observaciones: Optional[str] = field(default=None)
    created_at: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.tipo_propiedad not in ("TERRENO", "EDIFICACION"):
            raise ValueError("Tipo de propiedad inválido.")
        if not self.cliente.strip():
            raise ValueError("Debe indicar el cliente.")
        if self.monto_reserva <= 0:
            raise ValueError("El monto de reserva debe ser positivo.")
        if self.estado not in ("ACTIVA","CANCELADA","CONFIRMADA"):
            raise ValueError("Estado de reserva inválido.")
