from __future__ import annotations

import pytest

from services.terreno_service import TerrenoService


def test_buscar_por_nomenclatura_not_found(test_database):
    svc = TerrenoService()
    assert svc.buscar_por_nomenclatura("XYZ-123") is None


def test_crear_con_nomenclatura_and_find(test_database):
    svc = TerrenoService()
    datos = {
        "nomenclatura": "ABC-001",
        "manzana": "A",
        "numero_lote": "1",
        "superficie": 100,
        "ubicacion": "Zona Norte",
        "observaciones": "Prueba",
    }
    new_id = svc.crear_con_nomenclatura(datos)
    assert isinstance(new_id, int) and new_id > 0
    t = svc.buscar_por_nomenclatura("ABC-001")
    assert t is not None
    assert t.id == new_id


def test_crear_con_nomenclatura_duplicate(test_database):
    svc = TerrenoService()
    datos = {
        "nomenclatura": "DUP-001",
        "manzana": "B",
        "numero_lote": "2",
        "superficie": 120,
    }
    svc.crear_con_nomenclatura(datos)
    with pytest.raises(ValueError):
        svc.crear_con_nomenclatura(datos)

