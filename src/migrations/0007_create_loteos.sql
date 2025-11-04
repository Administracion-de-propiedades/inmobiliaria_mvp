-- Loteos con datos básicos
CREATE TABLE IF NOT EXISTS loteos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  ubicacion TEXT,
  municipio TEXT,
  provincia TEXT,
  fecha_inicio TEXT,        -- ISO yyyy-mm-dd
  fecha_fin TEXT,           -- ISO yyyy-mm-dd
  estado TEXT DEFAULT 'ACTIVO', -- ACTIVO | PAUSADO | CERRADO
  observaciones TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_loteos_nombre ON loteos(nombre);
CREATE INDEX IF NOT EXISTS idx_loteos_estado ON loteos(estado);

