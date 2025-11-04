import pytest
from services.reserva_service import ReservaService
from services.terreno_service import TerrenoService
from services.edificacion_service import EdificacionService


def test_reserva_service_flow_terreno():
    ts = TerrenoService()
    es = EdificacionService()
    rs = ReservaService()

    # terreno válido
    tid = ts.crear({"manzana": "R", "numero_lote": "2", "superficie": 180.0})

    # crear
    rid = rs.crear(
        {
            "tipo_propiedad": "TERRENO",
            "propiedad_id": tid,
            "cliente": "Cliente Test",
            "fecha_reserva": "2025-11-04",
            "monto_reserva": 75000.0,
        }
    )
    assert rid > 0

    # confirmar
    rs.confirmar(rid)
    r = rs.obtener(rid)
    assert r is not None and r.estado == "CONFIRMADA"

    # cancelar
    rs.cancelar(rid)
    r = rs.obtener(rid)
    assert r is not None and r.estado == "CANCELADA"

    # actualizar
    rs.actualizar(rid, {"monto_reserva": 80000.0})
    r = rs.obtener(rid)
    assert r is not None and r.monto_reserva == 80000.0

    # eliminar
    rs.eliminar(rid)
    assert rs.obtener(rid) is None


def test_reserva_service_validaciones_edificacion():
    ts = TerrenoService()
    es = EdificacionService()
    rs = ReservaService()

    # edificación válida
    eid = es.crear({"tipo": "CASA", "superficie_cubierta": 95.0})

    # ok
    rid = rs.crear(
        {
            "tipo_propiedad": "EDIFICACION",
            "propiedad_id": eid,
            "cliente": "Otro Cliente",
            "fecha_reserva": "2025-11-04",
            "monto_reserva": 100000.0,
        }
    )
    assert rid > 0

    # propiedad inexistente
    with pytest.raises(Exception):
        rs.crear(
            {
                "tipo_propiedad": "EDIFICACION",
                "propiedad_id": 999999,
                "cliente": "X",
                "fecha_reserva": "2025-11-04",
                "monto_reserva": 1.0,
            }
        )

    # monto inválido
    with pytest.raises(Exception):
        rs.crear(
            {
                "tipo_propiedad": "EDIFICACION",
                "propiedad_id": eid,
                "cliente": "X",
                "fecha_reserva": "2025-11-04",
                "monto_reserva": 0.0,
            }
        )

