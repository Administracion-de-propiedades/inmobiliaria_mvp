-- Agrega FK opcional: terreno -> loteo
ALTER TABLE terrenos ADD COLUMN loteo_id INTEGER REFERENCES loteos(id) ON DELETE SET NULL ON UPDATE CASCADE;
CREATE INDEX IF NOT EXISTS idx_terreno_loteo ON terrenos(loteo_id);

