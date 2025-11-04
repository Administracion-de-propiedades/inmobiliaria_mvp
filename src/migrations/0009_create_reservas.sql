CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_propiedad TEXT NOT NULL CHECK (tipo_propiedad IN ('TERRENO', 'EDIFICACION')),
    propiedad_id INTEGER NOT NULL,
    cliente TEXT NOT NULL,
    fecha_reserva TEXT NOT NULL, -- ISO yyyy-mm-dd
    monto_reserva REAL NOT NULL CHECK (monto_reserva > 0),
    estado TEXT DEFAULT 'ACTIVA', -- ACTIVA | CANCELADA | CONFIRMADA
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reserva_tipo_propiedad ON reservas(tipo_propiedad, propiedad_id);
CREATE INDEX IF NOT EXISTS idx_reserva_estado ON reservas(estado);

