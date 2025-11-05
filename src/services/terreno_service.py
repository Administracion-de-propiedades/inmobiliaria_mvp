from __future__ import annotations

from typing import List, Optional, Literal

from entities.terreno import Terreno
from repositories.terreno_repository import TerrenoRepository


EstadoTerreno = Literal["DISPONIBLE", "RESERVADO", "VENDIDO"]


class TerrenoService:
    """Lógica de negocio para Terreno: validaciones, búsquedas y estados."""

    def __init__(self, repo: Optional[TerrenoRepository] = None) -> None:
        self.repo = repo or TerrenoRepository()

    # ---------- Validaciones ----------
    def _validate(self, t: Terreno) -> None:
        if not t.manzana or not t.numero_lote:
            raise ValueError("manzana y numero_lote son obligatorios.")
        if t.superficie is None or t.superficie <= 0:
            raise ValueError("superficie debe ser > 0.")
        if t.estado not in ("DISPONIBLE", "RESERVADO", "VENDIDO"):
            raise ValueError("estado inválido.")

    def _exists_duplicate(self, manzana: str, numero_lote: str, exclude_id: Optional[int] = None) -> bool:
        all_rows = self.repo.find_all()
        for r in all_rows:
            if r.manzana == manzana and r.numero_lote == numero_lote and r.id != exclude_id:
                return True
        return False

    # ---------- API ----------
    def crear(self, datos: dict) -> int:
        """Crea un Terreno validando duplicados (manzana+numero_lote)."""
        t = Terreno(**datos)
        self._validate(t)
        if self._exists_duplicate(t.manzana, t.numero_lote):
            raise ValueError("Ya existe un terreno con esa manzana y número de lote.")
        return self.repo.create(t)

    def actualizar(self, terreno_id: int, datos: dict) -> None:
        actual = self.repo.find_by_id(terreno_id)
        if not actual:
            raise ValueError("Terreno no encontrado.")
        for k, v in datos.items():
            setattr(actual, k, v)
        self._validate(actual)
        if self._exists_duplicate(actual.manzana, actual.numero_lote, exclude_id=actual.id):
            raise ValueError("Otro terreno con la misma manzana y número de lote ya existe.")
        self.repo.update(actual)

    def obtener(self, terreno_id: int) -> Optional[Terreno]:
        return self.repo.find_by_id(terreno_id)

    def listar(self) -> List[Terreno]:
        return self.repo.find_all()

    def listar_disponibles(self) -> List[Terreno]:
        return self.repo.list_disponibles()

    def eliminar(self, terreno_id: int) -> None:
        """Eliminación simple. (Más adelante: baja lógica si se requiere.)"""
        self.repo.delete(terreno_id)

    # ---------- Búsquedas ----------
    def buscar_por_nomenclatura(self, nomenclatura: str) -> Optional[Terreno]:
        """Devuelve un Terreno por nomenclatura exacta; None si no existe o string vacío."""
        return self.repo.find_by_nomenclatura(nomenclatura)

    # ---------- Crear con nomenclatura (desde diálogo) ----------
    def crear_con_nomenclatura(self, datos_minimos: dict) -> int:
        """
        Crea un Terreno con un set mínimo de datos que incluye 'nomenclatura'.
        Requiere: manzana (str), numero_lote (str), superficie (float>0), nomenclatura (str).
        """
        nom = str(datos_minimos.get("nomenclatura") or "").strip()
        if not nom:
            raise ValueError("La nomenclatura es obligatoria.")
        if self.repo.find_by_nomenclatura(nom):
            raise ValueError("Ya existe un terreno con esa nomenclatura.")

        payload = {
            "manzana": str(datos_minimos.get("manzana") or "").strip(),
            "numero_lote": str(datos_minimos.get("numero_lote") or "").strip(),
            "superficie": float(str(datos_minimos.get("superficie") or "0").replace(",", ".")),
            "ubicacion": (str(datos_minimos.get("ubicacion") or "").strip() or None),
            "observaciones": (str(datos_minimos.get("observaciones") or "").strip() or None),
            "nomenclatura": nom,
            "estado": "DISPONIBLE",
        }
        return self.crear(payload)

    # ---------- Reglas de estado ----------
    def cambiar_estado(self, terreno_id: int, nuevo_estado: EstadoTerreno) -> None:
        t = self.repo.find_by_id(terreno_id)
        if not t:
            raise ValueError("Terreno no encontrado.")
        if nuevo_estado not in ("DISPONIBLE", "RESERVADO", "VENDIDO"):
            raise ValueError("estado inválido.")
        if t.estado == "VENDIDO" and nuevo_estado != "VENDIDO":
            raise ValueError("No se puede revertir un terreno VENDIDO.")
        if nuevo_estado == "RESERVADO" and t.estado != "DISPONIBLE":
            raise ValueError("Sólo se puede reservar un terreno DISPONIBLE.")
        t.estado = nuevo_estado
        self.repo.update(t)

