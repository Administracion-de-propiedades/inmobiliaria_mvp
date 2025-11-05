-- Índice único parcial para evitar duplicados de nomenclatura (si no es NULL)
CREATE UNIQUE INDEX IF NOT EXISTS ux_terrenos_nomenclatura
ON terrenos(nomenclatura)
WHERE nomenclatura IS NOT NULL;

