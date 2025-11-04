CREATE TABLE IF NOT EXISTS terrenos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manzana TEXT,
    numero_lote TEXT,
    superficie REAL,
    ubicacion TEXT,
    nomenclatura TEXT,
    estado TEXT DEFAULT 'DISPONIBLE'
);

