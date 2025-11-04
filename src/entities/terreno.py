from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

EstadoTerreno = Literal["DISPONIBLE", "RESERVADO", "VENDIDO"]


@dataclass
class Terreno:
    """
    Representa un lote/terreno dentro de un loteo o zona.
    Debe ser coherente con la tabla 'terrenos'.
    """

    id: Optional[int] = field(default=None)
    manzana: str = field(default="")
    numero_lote: str = field(default="")
    superficie: float = field(default=0.0)  # en m2 por defecto
    unidad_medida: str = field(default="m2")  # 'm2' por defecto
    ubicacion: Optional[str] = field(default=None)  # dirección/descr.
    nomenclatura: Optional[str] = field(default=None)  # catastral
    estado: EstadoTerreno = field(default="DISPONIBLE")
    observaciones: Optional[str] = field(default=None)
    created_at: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        if not self.manzana:
            raise ValueError("El campo 'manzana' es obligatorio.")
        if not self.numero_lote:
            raise ValueError("El campo 'numero_lote' es obligatorio.")
        if self.superficie is None or self.superficie <= 0:
            raise ValueError("La 'superficie' debe ser > 0.")
        if self.unidad_medida.strip().lower() not in {"m2", "m²", "mt2", "mtrs2"}:
            # normalizamos, pero permitimos variantes comunes
            self.unidad_medida = "m2"
        if self.estado not in ("DISPONIBLE", "RESERVADO", "VENDIDO"):
            raise ValueError("Estado inválido para Terreno.")

    def display_name(self) -> str:
        """Etiqueta corta para listas/tablas (ej. 'Mz A – Lote 12')."""
        return f"Mz {self.manzana} – Lote {self.numero_lote}".strip()

