<div align="center">

# 🔒 KR-CLI DOMINION

### **La Herramienta de IA Más Avanzada para Ciberseguridad**

[![Version](https://img.shields.io/badge/version-5.3.46-blue.svg)](https://pypi.org/project/kr-cli-dominion/)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Kali%20%7C%20Termux-red.svg)]()

**Asistente IA especializado en pentesting, análisis de vulnerabilidades y operaciones de seguridad ofensiva**

[🚀 Instalación](#-instalación-rápida) • [✨ Características](#-características-principales) • [📖 Uso](#-uso) • [💎 Planes](#-planes-y-precios)

---

</div>

## 🎯 ¿Qué es KR-CLI DOMINION?

**KR-CLI DOMINION** es una herramienta de línea de comandos potenciada por IA que transforma tu terminal en un centro de operaciones de ciberseguridad. Diseñada específicamente para profesionales de seguridad, pentesters y entusiastas de hacking ético.

### 🔥 ¿Por qué KR-CLI?

- **IA Especializada**: Modelo entrenado específicamente en ciberseguridad, no una IA genérica
- **Respuestas Contextuales**: Entiende comandos de Kali, Metasploit, Nmap y más
- **Multiplataforma**: Funciona en Kali Linux, Termux (Android) y cualquier distribución Linux
- **Interfaz Profesional**: Terminal con colores, animaciones y experiencia premium
- **Búsqueda Web Integrada**: Consulta información en tiempo real mientras trabajas

---

## ✨ Características Principales

### 🤖 **Asistente IA Avanzado**
- Análisis de comandos de pentesting
- Explicación de vulnerabilidades y CVEs
- Generación de scripts personalizados
- Recomendaciones de herramientas

### 🔍 **Búsqueda Web en Tiempo Real**
- Integración con DuckDuckGo
- Búsqueda de CVEs y exploits
- Noticias de ciberseguridad actualizadas
- Enriquecimiento automático de respuestas

### 🛠️ **Modo Agente**
- Creación automática de scripts Python/Bash
- Scaffolding de proyectos (Pentest, CTF, Audit)
- Generación de reportes profesionales
- Planificación de auditorías

### 🔐 **Sistema de Autenticación**
- Registro y login seguro con Supabase
- Gestión de créditos y suscripciones
- Planes Free y Premium
- Pagos con criptomonedas (NowPayments)

### 🎨 **Interfaz Premium**
- Animación Matrix al inicio
- Colores cyberpunk (azul/cyan)
- Menús interactivos intuitivos
- Experiencia de usuario pulida

---

## 🚀 Instalación Rápida

### **Opción 1: Instalación con pip (Recomendado)**

```bash
# Instalar desde PyPI
pip install kr-cli-dominion

# Ejecutar
kr-cli
```

### **Opción 2: Instalación desde código fuente**

```bash
# Clonar repositorio
git clone https://github.com/kalirootcode/KaliRootCLI.git
cd KaliRootCLI

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python -m kalirootcli
```

### **Opción 3: Instalación en Termux (Android)**

```bash
# Actualizar paquetes
pkg update && pkg upgrade

# Instalar dependencias del sistema
pkg install python libxml2 libxslt clang cmake rust build-essential binutils

# Instalar KR-CLI
pip install kr-cli-dominion

# Ejecutar
kr-cli
```

---

## ⚙️ Configuración Inicial

### 1. **Crear Cuenta**

Al ejecutar por primera vez, selecciona **"Registrarse"**:

```
📝 REGISTRO DE USUARIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 Email: tu@email.com
👤 Username: tunombre
🔐 Password: ******

✅ ¡Registro exitoso!
📧 Revisa tu email para verificar tu cuenta
```

### 2. **Verificar Email**

- Revisa tu bandeja de entrada (y spam)
- Haz clic en el enlace de verificación
- Regresa a KR-CLI e inicia sesión

### 3. **Iniciar Sesión**

```bash
# Ejecutar KR-CLI
kr-cli

# Seleccionar "Iniciar Sesión"
📧 Email: tu@email.com
🔐 Password: ******

✅ Sesión iniciada correctamente
```

---

## 📖 Uso

### **Menú Principal**

```
╔═══════════════════════════════════════════════════════════╗
║              KR-CLI DOMINION v3.5 (5.3.46)               ║
╚═══════════════════════════════════════════════════════════╝

1 › 🤖 Consola IA          Asistente de ciberseguridad
2 › 🛠️  Modo Agente         Crear scripts y proyectos
3 › 💎 Tienda              Comprar créditos/Premium
4 › 👤 Mi Cuenta           Ver perfil y créditos
0 › 🚪 Salir               Cerrar sesión
```

### **1. Consola IA - Asistente Inteligente**

Haz preguntas sobre ciberseguridad, comandos, vulnerabilidades:

```
🤖 DOMINION › ¿Cómo usar nmap para escanear puertos?

💡 Para escanear puertos con Nmap:

1. Escaneo básico:
   nmap 192.168.1.1

2. Escaneo de puertos específicos:
   nmap -p 80,443,8080 192.168.1.1

3. Escaneo completo (todos los puertos):
   nmap -p- 192.168.1.1

4. Detección de servicios y versiones:
   nmap -sV 192.168.1.1

5. Escaneo sigiloso (SYN scan):
   nmap -sS 192.168.1.1
```

**Comandos especiales:**
- `/search <query>` - Buscar en la web
- `/news [topic]` - Noticias de ciberseguridad
- `/cve <CVE-ID>` - Información de vulnerabilidades
- `/websearch` - Activar/desactivar búsqueda automática

### **2. Modo Agente - Automatización**

Crea scripts y proyectos automáticamente:

```
🛠️  MODO AGENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1 › 📝 Crear Script        Python o Bash desde plantillas
2 › 📁 Crear Proyecto      Pentest, CTF o Audit
3 › 📋 Planificador        Gestión de proyectos
```

**Ejemplo - Crear Proyecto Pentest:**
```
📁 Nombre del proyecto: audit-empresa-2024
📝 Descripción: Auditoría de seguridad completa

✅ Proyecto creado en: ~/kalirootcli_projects/audit-empresa-2024/

Estructura:
├── recon/          # Reconocimiento
├── scan/           # Escaneos
├── exploit/        # Explotación
├── post/           # Post-explotación
├── reports/        # Reportes
└── notes.md        # Notas del proyecto
```

### **3. Tienda - Créditos y Premium**

```
💎 TIENDA KR-CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAQUETES DE CRÉDITOS:
💳 200 créditos  ────────────────────────────  $10 USD
💳 500 créditos  ────────────────────────────  $20 USD
💳 1200 créditos ────────────────────────────  $35 USD

SUSCRIPCIÓN PREMIUM:
👑 Premium Mensual ──────────────────────────  $20/mes
   ✓ Créditos ilimitados
   ✓ IA más potente (GPT-4 level)
   ✓ Soporte prioritario
   ✓ Funciones exclusivas
```

---

## 💎 Planes y Precios

| Característica | 🆓 Free | 👑 Premium |
|----------------|---------|------------|
| **Consultas IA** | 5 créditos iniciales | ✅ Ilimitadas |
| **Calidad de Respuestas** | Estándar (Llama 3.1 8B) | 🔥 Avanzada (Llama 3.3 70B) |
| **Búsqueda Web** | ✅ Incluida | ✅ Incluida |
| **Modo Agente** | ✅ Incluido | ✅ Incluido |
| **Soporte** | Comunidad | 💬 Prioritario |
| **Precio** | Gratis | $20/mes |

### 💳 **Métodos de Pago**

Aceptamos criptomonedas a través de NowPayments:
- Bitcoin (BTC)
- Ethereum (ETH)
- USDT (TRC20/ERC20)
- Y más de 150 criptomonedas

---

## 🔧 Solución de Problemas

### **Error: "No module named 'kalirootcli'"**
```bash
# Reinstalar el paquete
pip uninstall kr-cli-dominion
pip install kr-cli-dominion
```

### **Error: "Authentication failed"**
- Verifica que hayas confirmado tu email
- Revisa tu bandeja de spam
- Intenta reenviar el email de verificación

### **Error en Termux: "Failed building wheel"**
```bash
# Instalar dependencias del sistema
pkg install python libxml2 libxslt clang cmake rust build-essential

# Reintentar instalación
pip install kr-cli-dominion
```

---

## 📚 Ejemplos de Uso

### **Análisis de Comandos**

```
🤖 › Explica este comando: nmap -sS -sV -O -p- 192.168.1.0/24

💡 Este comando realiza un escaneo completo de red:

• -sS: SYN Scan (sigiloso, no completa conexión TCP)
• -sV: Detección de versiones de servicios
• -O: Detección de sistema operativo
• -p-: Escanea todos los 65535 puertos
• 192.168.1.0/24: Rango de red completo (256 IPs)

⚠️ ADVERTENCIA: Este escaneo es muy ruidoso y puede ser detectado.
```

### **Consulta de CVEs**

```
🤖 › /cve CVE-2024-3094

🔍 Buscando información sobre CVE-2024-3094...

📋 CVE-2024-3094 - XZ Utils Backdoor

Severidad: 🔴 CRÍTICA (CVSS 10.0)
Fecha: 29 de marzo de 2024

Descripción:
Backdoor malicioso en las versiones 5.6.0 y 5.6.1 de XZ Utils
que permite ejecución remota de código en servidores SSH.

Sistemas Afectados:
• Debian Sid
• Fedora 40/41
• Arch Linux (rolling)

Mitigación:
Actualizar a XZ Utils 5.4.6 o anterior inmediatamente.
```

### **Generación de Scripts**

```
🛠️ Modo Agente › Crear Script

📝 Nombre: port_scanner.py
📋 Descripción: Escáner de puertos básico con threading

✅ Script creado: ~/kalirootcli_projects/scripts/port_scanner.py

El script incluye:
• Threading para escaneo rápido
• Manejo de errores
• Output colorizado
• Logging de resultados
```

---

## 🛡️ Responsabilidad y Uso Ético

> **⚠️ IMPORTANTE**: KR-CLI DOMINION es una herramienta profesional diseñada para:
> - Pruebas de penetración autorizadas
> - Auditorías de seguridad legítimas
> - Educación en ciberseguridad
> - Investigación ética

**El uso de esta herramienta es responsabilidad EXCLUSIVA del usuario.**

Debes:
- ✅ Tener autorización explícita por escrito
- ✅ Usar solo en sistemas propios o autorizados
- ✅ Cumplir con las leyes locales e internacionales

**Los creadores NO se hacen responsables por mal uso.**

---

## 🤝 Soporte y Comunidad

### **¿Necesitas Ayuda?**

- 📧 **Email**: kalirootcode@proton.me
- 🐛 **Issues**: [GitHub Issues](https://github.com/kalirootcode/KaliRootCLI/issues)
- 📖 **Documentación**: [Wiki](https://github.com/kalirootcode/KaliRootCLI/wiki)

### **Contribuir**

¡Las contribuciones son bienvenidas!

```bash
# Fork el repositorio
git clone https://github.com/tu-usuario/KaliRootCLI.git

# Crear rama
git checkout -b feature/nueva-funcionalidad

# Commit y push
git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# Crear Pull Request
```

---

## 📜 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 🌟 Roadmap

### **Próximas Características**

- [ ] Integración con Metasploit Framework
- [ ] Generación automática de reportes PDF
- [ ] Modo colaborativo (equipos)
- [ ] Integración con Burp Suite
- [ ] Plugin system para extensiones
- [ ] Soporte para más LLMs (GPT-4, Claude)

---

<div align="center">

### **¿Listo para Revolucionar tu Workflow de Seguridad?**

```bash
pip install kr-cli-dominion
kr-cli
```

**Hecho con 💀 por el equipo de KaliRootCode**

[![GitHub](https://img.shields.io/badge/GitHub-KaliRootCLI-black?logo=github)](https://github.com/kalirootcode/KaliRootCLI)
[![PyPI](https://img.shields.io/badge/PyPI-kr--cli--dominion-blue?logo=pypi)](https://pypi.org/project/kr-cli-dominion/)

</div>
