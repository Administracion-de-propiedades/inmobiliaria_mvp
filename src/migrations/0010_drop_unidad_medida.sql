-- Remove 'unidad_medida' column from 'terrenos'
-- Requires SQLite >= 3.35 for DROP COLUMN support
ALTER TABLE terrenos DROP COLUMN unidad_medida;

