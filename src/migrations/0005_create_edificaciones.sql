-- Migración #0005: creación de tabla edificaciones
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS edificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,                            -- opcional (ej: “Casa frente 1”)
    tipo TEXT NOT NULL,                     -- CASA, DUPLEX, DEPARTAMENTO, LOCAL, GALPON, ETC
    superficie_cubierta REAL,               -- m² cubiertos
    ambientes INTEGER,                      -- total de ambientes
    habitaciones INTEGER,
    banios INTEGER,                         -- usar ASCII (banios) para compatibilidad
    cochera BOOLEAN DEFAULT 0,
    patio BOOLEAN DEFAULT 0,
    pileta BOOLEAN DEFAULT 0,
    estado TEXT DEFAULT 'DISPONIBLE',       -- DISPONIBLE | RESERVADO | VENDIDO
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_edif_tipo ON edificaciones(tipo);
CREATE INDEX IF NOT EXISTS idx_edif_estado ON edificaciones(estado);

