# 🔄 Estado de Sincronización Web-CLI: Análisis Completo

**Fecha:** 12 de marzo 2026  
**Estado:** 60% Implementado - Requiere SQL setup final

---

## 📊 Resumen Ejecutivo

La sincronización está **parcialmente implementada**:

| Componente | Estado | Detalles |
|-----------|--------|----------|
| CLI → Supabase | ✅ 90% | Escribe en `cli_chat_history`, falta mapeo usuario |
| Dashboard → Lectura | ✅ 90% | Lee conversaciones, falta tabla `profiles` |
| Tablas Base de Datos | ⚠️ 50% | `cli_chat_history` existe, `profiles` NO existe |
| Auto-actualización | ❌ 0% | `total_queries` no se actualiza automáticamente |
| Triggers de Sincronización | ❌ 0% | Falta crear triggers en BD |

---

## 🔍 Lo que YA está funcionando

### 1️⃣ CLI Escribe Conversaciones ✅

**Archivo:** `kalirootcli/ai_handler.py` línea 177

```python
save_chat_interaction(self.user_id, query, raw_text)
```

**¿Qué hace?**
- Cuando usuario hace query en CLI
- Se llama `save_chat_interaction()` 
- Se inserta en tabla `cli_chat_history`
- Con campos: `user_id, role ('user'/'assistant'), content, created_at`

**Tabla:** `cli_chat_history`
```
id (UUID)
user_id (UUID) → Referencia al usuario
role (TEXT) → 'user' o 'assistant'
content (TEXT) → El mensaje
created_at (TIMESTAMP)
```

### 2️⃣ Dashboard Lee Conversaciones ✅

**Archivo:** `/web/dashboard-new.html` línea 745

```javascript
async function loadConversations() {
    const { data } = await window.KRSupabase.supabase
        .from('cli_chat_history')
        .select('*')
        .eq('user_id', currentUser.id)
        .order('created_at', { ascending: false })
        .limit(50);
    
    userConversations = data || [];
}
```

**¿Qué hace?**
- Dashboard carga conversaciones del usuario
- Las filtra por `user_id`
- Las limita a últimas 50
- Las ordena por fecha

### 3️⃣ Dashboard Analiza & Genera Sugerencias ✅

**Archivo:** `/web/dashboard-new.html` línea 795

```javascript
function analyzeConversations() {
    const suggestions = [];
    const contentLower = userConversations
        .map(c => c.content.toLowerCase())
        .join(' ');

    if (contentLower.includes('metasploit')) {
        suggestions.push('🎯 ¡Avanzaste en Metasploit!...');
    }
    // ... más análisis
}
```

**¿Qué hace?**
- Detecta keywords: metasploit, osint, nmap, exploit, malware
- Genera mensajes personalizados
- Motiva basado en cantidad de queries (10+, 50+, 100+)
- Muestra en terminal output

---

## ❌ Lo que FALTA

### 1️⃣ Tabla `profiles` NO Existe

**Problema:** Dashboard intenta de leer de tabla `profiles` que no existe

**Línea 703 de dashboard-new.html:**
```javascript
const { data: profile } = await window.KRSupabase.supabase
    .from('profiles')  // ← ESTA TABLA NO EXISTE
    .select('*')
    .eq('id', currentUser.id)
    .single();
```

**Necesita:**
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY → auth.users.id
  username TEXT
  email TEXT
  kr_balance INTEGER
  total_queries INTEGER
  cli_initialized BOOLEAN
  initialized_at TIMESTAMP
  created_at TIMESTAMP
)
```

### 2️⃣ Desconexión de Usuarios

**Problema:** CLI usa `cli_users`, Web usa `profiles` (o auth.users)

```
CLI:  user_id → cli_users.id
Web: id → auth.users.id → (debería ser) profiles.id
```

**Impacto:** 
- Dashboard no sabe si CLI está inicializado
- No puede mostrar KR balance
- No puede contar queries

### 3️⃣ Sin Auto-actualización de Stats

**Problema:** `total_queries` en `profiles` es manual

Actualmente:
```javascript
profile.total_queries || 0  // ← Valor estático
```

Debería ser:
- Trigger en BD que cuente `cli_chat_history` 
- O API que actualice en tiempo real

**Falta:**
```sql
CREATE TRIGGER auto_update_queries
AFTER INSERT ON cli_chat_history
FOR EACH ROW
UPDATE profiles SET total_queries = total_queries + 1
WHERE id = NEW.user_id;
```

### 4️⃣ Sin Trigger Auto-Crear Perfil

**Problema:** Cuando usuario se registra en web, no hay perfil

**Debería existir:**
```sql
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
INSERT INTO profiles (...) VALUES (...);
```

---

## 🚀 PLAN PARA COMPLETAR SINCRONIZACIÓN

### PASO 1: Ejecutar SQL Setup (5 min)

Archivo: `SQL_WEB_CLI_SYNC_SETUP.sql`

Contiene:
- ✅ CREATE TABLE profiles
- ✅ CREATE TRIGGER total_queries auto-increment
- ✅ CREATE TRIGGER auto-crear profile
- ✅ CREATE RLS policies
- ✅ Verificación de datos

**Acción:** Copia todo a Supabase SQL Editor y ejecuta

### PASO 2: Actualizar Dashboard (2 min)

El dashboard CASI funciona, solo necesita:
- ✅ Cambiar `profiles.username` → se usa igual
- ✅ Cambiar `profiles.kr_balance` → se usa igual
- ✅ Cambiar `profiles.cli_initialized` → se usa igual

**Acción:** Ya está listo, no necesita cambios

### PASO 3: Actualizar CLI (5 min)

El CLI necesita cambiar qué tabla usa para perfil:

**Actualmente en `database_manager.py` línea ~210:**
```python
# Usa cli_users (antiguo)
result = supabase.table("cli_users")...
```

**Debería ser:**
```python
# Nuevo: usar profiles
result = supabase.table("profiles")...
```

**Impacto:** ~5 líneas a cambiar en varios archivos

### PASO 4: Crear Usuario de Prueba (2 min)

1. Registrar usuario en web
2. Ejecutar query en CLI
3. Ver que aparece en dashboard

---

## 📋 Checklist: Qué Ejecutar

```sql
-- Copia y ejecuta en Supabase SQL Editor:

1. CREATE profiles table ✅
2. CREATE trigger total_queries ✅
3. CREATE trigger auto-create profile ✅
4. CREATE RLS policies ✅
5. Verify: SELECT * FROM profiles ✅
```

---

## 🔧 Modificaciones de Código Necesarias

### Opción A: Mínima (Recomendada)

Cambios pequeños en CLI para mapeo de usuario:

**Archivo:** `kalirootcli/database_manager.py`

```python
# Línea ~210
# DE:
result = supabase.table("cli_users").select(...)

# A:
result = supabase.table("profiles").select(...)
```

**Impacto:** 2-3 cambios
**Tiempo:** 5 min
**Riesgo:** Bajo

### Opción B: Completa (Futura)

Migrar completamente a tabla única `profiles`:
- Unificar `cli_users` y `profiles`
- Crear migración de datos
- Actualizar todos los references

**Impacto:** 10+ cambios
**Tiempo:** 30 min
**Riesgo:** Medio

---

## 📊 Resultado Esperado Después

### ✅ Flujo Completo:

```
1. Usuario registra en WEB
   ↓ (trigger)
2. Auto-crea profile en BD
   ↓
3. Dashboard muestra perfil (username, KR balance)
   ↓
4. Descargar instalador & ejecutar install.sh
   ↓ 
5. CLI sincroniza con mismo user_id
   ↓
6. CLI hace query → save_chat_interaction()
   ↓ (trigger)
7. total_queries incrementa automáticamente
   ↓
8. Dashboard recarga → ve conversación nueva
   ↓
9. Analiza y genera sugerencia personalizada
   ↓
10. ¡Terminal output muestra insights activos!
```

---

## 📝 Ejemplo de Datos Después

**En `profiles` table:**
```
id         | username | kr_balance | total_queries | cli_initialized | 
uuid-123   | rk13     | 250        | 5             | true            |
```

**En `cli_chat_history` table:**
```
id     | user_id   | role      | content
uuid-1 | uuid-123  | user      | ¿Qué es Metasploit?
uuid-2 | uuid-123  | assistant | Metasploit es un framework...
uuid-3 | uuid-123  | user      | Cómo usar nmap?
uuid-4 | uuid-123  | assistant | Nmap es una herramienta...
```

**Dashboard Output:**
```
>>> ./krm --user=rk13 --sync-on
✓ Sincronización exitosa

> Analizando historial...

🎯 ¡Avanzaste bastante en Metasploit! Los profesionales...

📱 Los escaneos con Nmap que practicas son fundamentales...

🔥 Ya tienes momentum. 5 consultas. Continúa practicando.
```

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### YA LISTO PARA EJECUTAR:

1. **`SQL_WEB_CLI_SYNC_SETUP.sql`** ← Copia y ejecuta TODO
   - Crea tabla profiles
   - Crea triggers
   - Crea RLS policies

2. **Sin cambios de código todavía** - Primero verifica BD

---

## ❓ FAQ

**P: ¿Es obligatorio cambiar el código del CLI?**  
R: No inmediatamente. El SQL setup funciona. El cambio de CLI es para optimización futura.

**P: ¿Los triggers se ejecutan automáticamente?**  
R: Sí, una vez creados en Supabase se ejecutan automáticamente.

**P: ¿Qué pasa si no ejecuto el SQL?**  
R: Dashboard fallará al cargar porque `profiles` no existe.

**P: ¿Puedo probar sin crear tabla `profiles`?**  
R: No, es requerida para que dashboard funcione.

---

## 🟢 STATUS

**Base de Datos:** ⚠️ INCOMPLETA (falta tabla profiles)
**Dashboard:** ✅ LISTO (esperando tabla)
**CLI:** ✅ LISTO (guarda conversaciones)
**Sincronización:** ⚠️ CASI LISTA (requiere SQL setup)

---

**Próximo:** Ejecuta `SQL_WEB_CLI_SYNC_SETUP.sql` en Supabase SQL Editor
