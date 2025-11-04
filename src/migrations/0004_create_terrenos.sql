-- Migración #0004: creación de tabla terrenos

CREATE TABLE IF NOT EXISTS terrenos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manzana TEXT NOT NULL,                 -- código o letra de la manzana
    numero_lote TEXT NOT NULL,             -- número o identificador dentro de la manzana
    superficie REAL NOT NULL,              -- m²
    unidad_medida TEXT DEFAULT 'm2',       -- unidad, por defecto m²
    ubicacion TEXT,                        -- descripción general o dirección
    nomenclatura TEXT,                     -- nomenclatura catastral o similar
    estado TEXT DEFAULT 'DISPONIBLE',      -- DISPONIBLE, RESERVADO, VENDIDO
    observaciones TEXT,                    -- notas adicionales
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

