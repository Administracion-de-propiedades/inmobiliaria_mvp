-- Migración #0006: creación de tabla puente N:M entre edificaciones y terrenos
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS edificacion_terreno (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edificacion_id INTEGER NOT NULL,
    terreno_id INTEGER NOT NULL,
    UNIQUE (edificacion_id, terreno_id),
    FOREIGN KEY (edificacion_id) REFERENCES edificaciones(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (terreno_id) REFERENCES terrenos(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_et_edificacion ON edificacion_terreno(edificacion_id);
CREATE INDEX IF NOT EXISTS idx_et_terreno ON edificacion_terreno(terreno_id);

