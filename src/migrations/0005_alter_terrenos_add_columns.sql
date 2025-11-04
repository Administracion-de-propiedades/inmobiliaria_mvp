-- Migración #0005: agrega columnas faltantes a terrenos
-- Añade unidad_medida, observaciones y created_at si no existían del esquema anterior

ALTER TABLE terrenos ADD COLUMN unidad_medida TEXT DEFAULT 'm2';
ALTER TABLE terrenos ADD COLUMN observaciones TEXT;
ALTER TABLE terrenos ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

