-- =====================================================
-- SQL para crear tabla de Términos y Condiciones
-- Ejecutar en Supabase SQL Editor
-- =====================================================

-- Crear tabla para guardar aceptación de términos
CREATE TABLE IF NOT EXISTS user_agreements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    agreement_text TEXT NOT NULL,  -- Guardamos el texto exacto que aceptaron como respaldo
    accepted BOOLEAN DEFAULT TRUE,
    accepted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT  -- Opcional, para mayor seguridad de auditoría
);

-- Habilitar RLS (Row Level Security) para seguridad
ALTER TABLE user_agreements ENABLE ROW LEVEL SECURITY;

-- Política: Los usuarios pueden ver sus propios acuerdos
CREATE POLICY "Users can view their own agreements" 
ON user_agreements FOR SELECT 
USING (auth.uid() = user_id);

-- Política: El servidor (service_role) puede insertar todos
-- Nota: En Supabase, el service_role se salta RLS, así que no es estrictamente necesaria 
-- una política de INSERT si usamos la key de servicio, pero es buena práctica.
