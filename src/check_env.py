from __future__ import annotations

from services.edificacion_service import EdificacionService
from services.terreno_service import TerrenoService


def main() -> None:
    print("\n=== TEST EDIFICACION SERVICE ===")
    trepo = TerrenoService()
    eid_svc = EdificacionService()

    # Asegurar 2 terrenos
    t1 = trepo.crear({"manzana": "S", "numero_lote": "1", "superficie": 180.0})
    t2 = trepo.crear({"manzana": "S", "numero_lote": "2", "superficie": 200.0})

    # Crear edificación DISPONIBLE sin vínculos
    eid = eid_svc.crear({"tipo": "CASA", "superficie_cubierta": 95.0})
    print("Creada (sin terrenos), id:", eid)

    # Intentar vender sin vínculos (debe fallar)
    try:
        eid_svc.cambiar_estado(eid, "VENDIDO")
    except Exception as e:  # pragma: no cover - quick env check
        print("Venta sin terrenos OK:", e)

    # Agregar terrenos y vender
    eid_svc.agregar_terreno(eid, t1)
    eid_svc.agregar_terreno(eid, t2)
    print("Terrenos tras agregar:", eid_svc.obtener(eid).terrenos_ids)

    eid_svc.cambiar_estado(eid, "RESERVADO")
    print("Estado tras reservar:", eid_svc.obtener(eid).estado)

    eid_svc.cambiar_estado(eid, "VENDIDO")
    print("Estado tras vender:", eid_svc.obtener(eid).estado)

    # Intentar quitar el último terreno en VENDIDO (debe fallar)
    try:
        eid_svc.reemplazar_terrenos(eid, [])
    except Exception as e:  # pragma: no cover - quick env check
        print("No quitar todos los terrenos en VENDIDO OK:", e)

    # Intentar eliminar VENDIDO (debe fallar)
    try:
        eid_svc.eliminar(eid)
    except Exception as e:  # pragma: no cover - quick env check
        print("No eliminar VENDIDO OK:", e)


if __name__ == "__main__":
    main()

# --- TEST Loteo (opcional) ---
from services.loteo_service import LoteoService
from services.terreno_service import TerrenoService as _TerrenoSvc

print("\n=== TEST LOTEO SERVICE ===")
ts = _TerrenoSvc()
ls = LoteoService()

# preparar terrenos
t1 = ts.crear({"manzana": "L1", "numero_lote": "A1", "superficie": 200.0})
t2 = ts.crear({"manzana": "L1", "numero_lote": "A2", "superficie": 210.0})

# crear loteo con terrenos
lid = ls.crear({"nombre": "Loteo Norte", "estado": "ACTIVO", "terrenos_ids": [t1, t2]})
print("Creado Loteo:", lid, ls.obtener(lid).terrenos_ids)

# desasignar uno
ls.reemplazar_terrenos(lid, [t2])
print("Asignación ahora:", ls.obtener(lid).terrenos_ids)

# actualizar datos
ls.actualizar(lid, {"municipio": "Neuquén", "provincia": "Neuquén"})
print("Municipio:", ls.obtener(lid).municipio)

# eliminar (debe desasignar primero)
ls.eliminar(lid)
print("Existe:", ls.obtener(lid))

