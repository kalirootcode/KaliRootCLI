-- =====================================================
-- SQL para agregar columna credits_amount a cli_payments
-- Ejecutar en Supabase SQL Editor
-- =====================================================

-- Agregar la columna credits_amount a la tabla cli_payments
ALTER TABLE cli_payments 
ADD COLUMN IF NOT EXISTS credits_amount INTEGER DEFAULT 0;

-- Verificar que se agregó correctamente
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'cli_payments' 
ORDER BY ordinal_position;
