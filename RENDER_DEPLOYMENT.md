# KR-CLI Backend - Deployment to Render

## 🚀 Deployment del Backend Principal

Este es el backend que maneja:
- Autenticación de usuarios (Supabase)
- Procesamiento de comandos con IA (Groq)
- Sistema de créditos y pagos (NowPayments)
- Gestión de sesiones y historial

---

## 📦 Paso 1: Preparar Render

### Crear Servicio en Render

1. **Ir a Render Dashboard**: https://dashboard.render.com
2. **New → Web Service**
3. **Conectar repositorio**: `KaliRootCLI`
4. **Configuración**:
   ```
   Name: kr-cli-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: . (raíz del proyecto)
   Runtime: Python 3
   Build Command: pip install -r requirements-server.txt
   Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

---

## 🔑 Paso 2: Configurar Variables de Entorno

En Render, ve a **Environment** y agrega:

```env
# Supabase
SUPABASE_URL=https://cvesmbgevcyrdbbftwvy.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2ZXNtYmdldmN5cmRiYmZ0d3Z5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0NzkyMTUsImV4cCI6MjA4MTA1NTIxNX0.FavKlhkCXj3iE0kHBGbQWfN86LVTUThBP0t40NacpPs
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN2ZXNtYmdldmN5cmRiYmZ0d3Z5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTQ3OTIxNSwiZXhwIjoyMDgxMDU1MjE1fQ.LNBjQYd4qpKHtndCgDdLtlQOqdRmXd0nO8c5FUa7dY8

# Groq AI
GROQ_API_KEY=tu_groq_api_key_aqui
GROQ_MODEL=llama-3.1-8b-instant

# NowPayments
NOWPAYMENTS_API_KEY=C3VZA57-3HGMGDP-NQYD18J-EB138HH
IPN_SECRET_KEY=TyFVWjsc39ER3PsQcaijmys9C/YnsTlx

# Config
DEFAULT_CREDITS_ON_REGISTER=5
LOG_LEVEL=INFO
```

---

## 🌐 Paso 3: Deploy

1. Click **Create Web Service**
2. Render automáticamente:
   - Clona el repo
   - Instala dependencias de `requirements-server.txt`
   - Inicia el servidor con uvicorn
3. Espera ~5-10 minutos
4. Tu API estará en: `https://kr-cli-backend.onrender.com`

---

## ✅ Paso 4: Verificar

```bash
# Health check
curl https://kr-cli-backend.onrender.com/health

# Test endpoint
curl https://kr-cli-backend.onrender.com/
```

---

## 🔗 Paso 5: Conectar con la Web

Una vez que tengas la URL del backend, actualiza la web:

1. **Editar** `web/js/config.js` o `web/js/supabase-client.js`
2. **Agregar** la URL del backend si es necesario
3. **Push** a GitHub

---

## 📋 Servicios en Render

Después de este deployment tendrás:

| Servicio | Puerto/URL | Propósito |
|----------|------------|-----------|
| **kr-cli-backend** | `https://kr-cli-backend.onrender.com` | Backend principal (auth, AI, pagos) |
| **kr-cli-education-api** | `https://kr-cli-education-api.onrender.com` | APIs educativas (news + education) |

---

## 💡 Optimización

### Plan Gratuito
- 750 horas/mes
- Se "duerme" después de 15 min inactividad
- Cold start: ~30 segundos

### Plan Starter ($7/mes)
- Siempre activo
- Sin cold starts
- Más recursos

---

## 🆘 Troubleshooting

### Error: Module not found
- Verifica que `requirements-server.txt` tenga todas las dependencias
- Revisa los logs en Render Dashboard

### Error: Port binding
- Render maneja el puerto automáticamente con `$PORT`
- No necesitas configurar puerto manualmente

### Error: Environment variables
- Verifica que todas las variables estén configuradas
- Usa los valores exactos de tu `.env` local

---

## 🎯 Resultado Final

Después del deployment:

- ✅ Backend principal en Render
- ✅ APIs educativas en Render
- ✅ Frontend en GitHub Pages
- ✅ Todo conectado y funcionando

**¡Sistema completo desplegado! 🚀**
