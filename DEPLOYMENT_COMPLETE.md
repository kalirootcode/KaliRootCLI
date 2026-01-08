# 🚀 KR-CLI - Deployment Completo

## ✅ Archivos Listos para Deployment

### Backend Principal
```
KaliRootCLI/
├── render.yaml              # Configuración de Render
├── RENDER_DEPLOYMENT.md     # Guía de deployment
├── requirements-server.txt  # Dependencias actualizadas
├── api_server.py           # Backend principal (FastAPI)
└── webhook_server.py       # Webhooks de pagos
```

### Backend Educativo (Web)
```
web/backend/
├── combined_api.py         # API unificada (News + Education)
├── requirements-web.txt    # Dependencias
└── render.yaml            # Configuración
```

---

## 📋 Plan de Deployment

### 1. Backend Principal (api_server.py)
```bash
# En Render Dashboard:
New Web Service → KaliRootCLI
Root Directory: . (raíz)
Build: pip install -r requirements-server.txt
Start: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

**Variables de entorno**: Las mismas que ya tienes en `.env`

### 2. Backend Educativo (combined_api.py)
```bash
# En Render Dashboard:
New Web Service → KaliRootCLI
Root Directory: web/backend
Build: pip install -r requirements-web.txt
Start: gunicorn --bind 0.0.0.0:$PORT --workers 2 combined_api:app
```

**Variables adicionales**: + GEMINI_API_KEY

### 3. Frontend (GitHub Pages)
Ya está configurado y pusheado ✅
- Actualizar `web/js/api-config.js` con URLs de Render
- Habilitar GitHub Pages en Settings

---

## 🔗 URLs Finales

| Servicio | URL | Propósito |
|----------|-----|-----------|
| **Backend Principal** | `https://kr-cli-backend.onrender.com` | Auth, AI, Pagos |
| **Backend Educativo** | `https://kr-cli-education-api.onrender.com` | News + Education |
| **Frontend Web** | `https://kalirootcode.github.io/KaliRootCLI/` | Interfaz web |

---

## 🎯 Próximos Pasos

1. **Commit y Push**:
   ```bash
   cd /home/rk13/RK13CODE/KaliRootCLI
   git add .
   git commit -m "Add Render deployment config for backend"
   git push origin main
   ```

2. **Deploy Backend Principal en Render**:
   - Seguir `RENDER_DEPLOYMENT.md`
   - Configurar variables de entorno
   - Deploy (~5-10 min)

3. **Deploy Backend Educativo en Render**:
   - Seguir `web/DEPLOYMENT.md`
   - Agregar GEMINI_API_KEY
   - Deploy (~5 min)

4. **Actualizar Frontend**:
   - Editar `web/js/api-config.js` con URLs reales
   - Push a GitHub
   - Habilitar GitHub Pages

---

## ✅ Checklist Final

- [x] Código web pusheado a GitHub
- [ ] Backend principal pusheado
- [ ] Servicio 1 en Render (backend principal)
- [ ] Servicio 2 en Render (backend educativo)
- [ ] GitHub Pages habilitado
- [ ] URLs actualizadas en frontend
- [ ] Testing completo

---

**¡Todo listo para deployment completo! 🚀**
