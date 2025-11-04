-- Add columns rol and activo to usuarios if not present
ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'USER';
ALTER TABLE usuarios ADD COLUMN activo BOOLEAN DEFAULT 1;

