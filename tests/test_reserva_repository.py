from entities.reserva import Reserva
from repositories.reserva_repository import ReservaRepository
from repositories.terreno_repository import TerrenoRepository
from entities.terreno import Terreno
from repositories.edificacion_repository import EdificacionRepository
from entities.edificacion import Edificacion


def test_reserva_repository_crud_terreno():
    rrepo = ReservaRepository()
    trepo = TerrenoRepository()

    # Precondición: Terreno
    tid = trepo.create(Terreno(manzana="T", numero_lote="1", superficie=150.0))

    # Create
    r = Reserva(
        tipo_propiedad="TERRENO",
        propiedad_id=tid,
        cliente="Juan Pérez",
        fecha_reserva="2025-11-04",
        monto_reserva=50000.0,
    )
    rid = rrepo.create(r)
    assert rid > 0

    # Read
    rdb = rrepo.find_by_id(rid)
    assert rdb is not None
    assert rdb.tipo_propiedad == "TERRENO"
    assert rdb.propiedad_id == tid
    assert rdb.cliente == "Juan Pérez"

    # Update
    rdb.monto_reserva = 60000.0
    rrepo.update(rdb)
    rdb2 = rrepo.find_by_id(rid)
    assert rdb2 is not None and rdb2.monto_reserva == 60000.0

    # List
    found = rrepo.find_all()
    assert any(x.id == rid for x in found)

    # Delete
    rrepo.delete(rid)
    assert rrepo.find_by_id(rid) is None


def test_reserva_repository_crud_edificacion():
    rrepo = ReservaRepository()
    erepo = EdificacionRepository()

    # Precondición: Edificación
    eid = erepo.create(Edificacion(tipo="CASA", superficie_cubierta=90.0))

    # Create
    r = Reserva(
        tipo_propiedad="EDIFICACION",
        propiedad_id=eid,
        cliente="María Gómez",
        fecha_reserva="2025-11-04",
        monto_reserva=120000.0,
    )
    rid = rrepo.create(r)
    assert rid > 0

    # Read & Delete
    assert rrepo.find_by_id(rid) is not None
    rrepo.delete(rid)
    assert rrepo.find_by_id(rid) is None

