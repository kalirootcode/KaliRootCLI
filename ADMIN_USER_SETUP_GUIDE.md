# 🔐 Crear Usuario Admin en Supabase

## 📋 Resumen Rápido

Se creará un nuevo usuario admin con:
- **Email:** `rk13sebaskrcli@admin.local`
- **Username:** `rk13sebaskrcli`
- **Password:** `AAaa11@@sebas`
- **Role:** `admin`

---

## ✅ INSTRUCCIONES PASO A PASO

### PASO 1: Abre Supabase Dashboard

1. Entra a https://app.supabase.com
2. Selecciona tu proyecto KaliRootCLI
3. Click en el menu izquierdo → **SQL Editor**

### PASO 2: Copia el SQL

Abre el archivo: `SQL_CREATE_ADMIN_USER.sql` en este directorio

O copia este SQL completo:

```sql
-- Crear tabla admin_users
CREATE TABLE IF NOT EXISTS public.admin_users (
  id uuid not null default gen_random_uuid (),
  email text not null,
  password_hash text not null,
  name text null default 'Admin'::text,
  role text null default 'admin'::text,
  last_login timestamp with time zone null,
  created_at timestamp with time zone null default now(),
  constraint admin_users_pkey primary key (id),
  constraint admin_users_email_key unique (email),
  constraint admin_users_role_check check (
    (role = any (array['admin'::text, 'superadmin'::text]))
  )
) TABLESPACE pg_default;

-- Crear nuevo usuario admin
INSERT INTO public.admin_users (
  email,
  password_hash,
  name,
  role,
  created_at
) VALUES (
  'rk13sebaskrcli@admin.local',
  crypt('AAaa11@@sebas', gen_salt('bf')),
  'RK13 Sebas',
  'admin',
  NOW()
)
ON CONFLICT (email) DO UPDATE SET
  password_hash = EXCLUDED.password_hash,
  name = EXCLUDED.name
RETURNING id, email, name, role, created_at;

-- Verificar que se creó
SELECT 
  id,
  email,
  name,
  role,
  created_at
FROM public.admin_users
WHERE email = 'rk13sebaskrcli@admin.local';
```

### PASO 3: Pega el SQL en Supabase

1. En **SQL Editor**, click en **New Query**
2. Pega todo el SQL anterior
3. Click en botón azul **Run** (o presiona Ctrl+Enter)

### PASO 4: Verifica la salida

Deberías ver algo como:

```
✅ Query successful
1 row inserted

id                                  | email                      | name      | role  | created_at
────────────────────────────────────┼────────────────────────────┼───────────┼───────┼──────────────────────
a1b2c3d4-e5f6-7890-abcd-ef1234567890| rk13sebaskrcli@admin.local | RK13 Sebas| admin | 2026-03-12T10:30:45Z
```

---

## 🔐 Credenciales para Login

Ahora puedes usar estas credenciales en la web:

```
Email:    rk13sebaskrcli@admin.local
Password: AAaa11@@sebas
```

**Login URL:** `http://localhost:8000/admin/`

---

## 🚀 Próximo Paso: Actualizar Auth en JavaScript

Para que el admin panel funcione con Supabase, necesitas actualizar el archivo:

**`/admin/js/supabase-admin.js`**

Asegúrate de que verifique credenciales contra la tabla `admin_users`:

```javascript
async login(email, password) {
    try {
        // Buscar usuario en admin_users
        const { data, error } = await this.supabase
            .from('admin_users')
            .select('*')
            .eq('email', email)
            .single();

        if (error || !data) {
            return { success: false, error: 'Usuario no encontrado' };
        }

        // Verificar contraseña (en servidor idealmente)
        const passwordMatch = await this.verifyPassword(password, data.password_hash);
        
        if (!passwordMatch) {
            return { success: false, error: 'Contraseña incorrecta' };
        }

        // Guardar sesión
        sessionStorage.setItem('admin_session', JSON.stringify({
            id: data.id,
            email: data.email,
            name: data.name,
            role: data.role
        }));

        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}
```

---

## 📝 Tabla admin_users - Schema

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | ID único (auto) |
| `email` | TEXT | Email único |
| `password_hash` | TEXT | Contraseña hasheada con bcrypt |
| `name` | TEXT | Nombre del admin |
| `role` | TEXT | 'admin' o 'superadmin' |
| `last_login` | TIMESTAMP | Última entrada |
| `created_at` | TIMESTAMP | Fecha creación |

---

## 🔒 Seguridad

✅ **Password Hashing:** Se usa `crypt()` con `bcrypt` (salt)  
✅ **Unique Email:** No hay emails duplicados  
✅ **Role Check:** Solo permite admin/superadmin  
✅ **Timestamp:** Registra cuándo se creó  

---

## ❓ FAQ

**P: ¿Cómo cambio la contraseña?**  
R: Ejecuta en SQL Editor:
```sql
UPDATE public.admin_users 
SET password_hash = crypt('NUEVA_PASSWORD', gen_salt('bf'))
WHERE email = 'rk13sebaskrcli@admin.local';
```

**P: ¿Cómo creo otro admin?**  
R: Repite el INSERT con diferente email.

**P: ¿Cómo elimino un admin?**  
R:
```sql
DELETE FROM public.admin_users 
WHERE email = 'rk13sebaskrcli@admin.local';
```

**P: ¿Cómo veo todos los admins?**  
R:
```sql
SELECT email, name, role, created_at, last_login 
FROM public.admin_users;
```

---

## 🎯 Siguientes Pasos

1. Ejecuta el SQL en Supabase ✅
2. Verifica que el usuario se creó ✅
3. Intenta hacer login con las credenciales
4. Accede a `/admin/panel-plus.html`
5. Configura los links de descarga
6. ¡Maneja el sistema!

---

**Archivo SQL:** `SQL_CREATE_ADMIN_USER.sql`  
**Credenciales:** Email: `rk13sebaskrcli@admin.local` | Pass: `AAaa11@@sebas`  
**Status:** 🟢 Listo para usar
