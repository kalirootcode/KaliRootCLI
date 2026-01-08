"""
Educational Platform Routes for KR-CLI API
Integrates directly with api_server.py via FastAPI Router
"""

from fastapi import APIRouter
from datetime import datetime

# ===== ROUTER =====
education_router = APIRouter(prefix="/api/education", tags=["Education"])
news_router = APIRouter(prefix="/api/news", tags=["News"])

# ===== EDUCATIONAL DATA =====
COURSES = [
    {
        "id": "fundamentals",
        "title": "Fundamentos de Ciberseguridad",
        "description": "Aprende los conceptos básicos de seguridad informática, terminología y metodologías de hacking ético.",
        "icon": "🎓",
        "difficulty": "beginner",
        "duration": "4 semanas",
        "modules": [
            {"id": "intro", "title": "Introducción al Hacking Ético", "labs": ["lab-nmap-basics"]},
            {"id": "networking", "title": "Fundamentos de Redes", "labs": ["lab-network-scan"]},
            {"id": "linux", "title": "Linux para Hackers", "labs": ["lab-linux-basics"]}
        ]
    },
    {
        "id": "reconnaissance",
        "title": "Reconocimiento y Enumeración",
        "description": "Técnicas avanzadas de recopilación de información y enumeración de objetivos.",
        "icon": "🔍",
        "difficulty": "intermediate",
        "duration": "3 semanas",
        "modules": [
            {"id": "passive", "title": "Reconocimiento Pasivo", "labs": ["lab-osint"]},
            {"id": "active", "title": "Reconocimiento Activo", "labs": ["lab-active-recon"]},
            {"id": "enum", "title": "Enumeración de Servicios", "labs": ["lab-service-enum"]}
        ]
    },
    {
        "id": "exploitation",
        "title": "Explotación de Vulnerabilidades",
        "description": "Aprende a explotar vulnerabilidades web, de sistema y de red de forma práctica.",
        "icon": "⚔️",
        "difficulty": "advanced",
        "duration": "5 semanas",
        "modules": [
            {"id": "web", "title": "Explotación Web", "labs": ["lab-sqli", "lab-xss"]},
            {"id": "system", "title": "Explotación de Sistemas", "labs": ["lab-metasploit"]},
            {"id": "privesc", "title": "Escalación de Privilegios", "labs": ["lab-privesc"]}
        ]
    },
    {
        "id": "post-exploitation",
        "title": "Post-Explotación",
        "description": "Técnicas de persistencia, movimiento lateral y exfiltración de datos.",
        "icon": "🎯",
        "difficulty": "advanced",
        "duration": "4 semanas",
        "modules": [
            {"id": "persistence", "title": "Técnicas de Persistencia", "labs": ["lab-persistence"]},
            {"id": "lateral", "title": "Movimiento Lateral", "labs": ["lab-pivoting"]},
            {"id": "exfil", "title": "Exfiltración de Datos", "labs": ["lab-exfiltration"]}
        ]
    }
]

LABS = {
    "lab-nmap-basics": {
        "id": "lab-nmap-basics",
        "title": "Tu Primer Escaneo con Nmap",
        "description": "Aprende a usar Nmap para descubrir hosts y servicios en una red.",
        "duration": "30 min",
        "difficulty": "beginner",
        "objectives": [
            "Entender los tipos de escaneos de Nmap",
            "Identificar puertos abiertos y servicios",
            "Interpretar los resultados del escaneo"
        ],
        "steps": [
            {
                "title": "Escaneo básico de puertos",
                "command": "nmap -sV 192.168.1.1",
                "explanation": "Este comando escanea los 1000 puertos más comunes y detecta versiones de servicios."
            },
            {
                "title": "Escaneo completo",
                "command": "nmap -sV -sC -p- 192.168.1.1",
                "explanation": "Escanea todos los puertos (65535), detecta versiones y ejecuta scripts por defecto."
            },
            {
                "title": "Escaneo sigiloso",
                "command": "nmap -sS -T2 --randomize-hosts 192.168.1.0/24",
                "explanation": "Escaneo SYN stealth con temporización lenta para evadir detección."
            }
        ],
        "resources": ["https://nmap.org/book/", "https://hackthebox.com"]
    },
    "lab-osint": {
        "id": "lab-osint",
        "title": "OSINT: Reconocimiento de Dominios",
        "description": "Técnicas de inteligencia de fuentes abiertas para recopilar información.",
        "duration": "45 min",
        "difficulty": "intermediate",
        "objectives": [
            "Usar herramientas OSINT",
            "Encontrar subdominios y emails",
            "Recopilar información pública"
        ],
        "steps": [
            {
                "title": "Búsqueda de subdominios",
                "command": "subfinder -d example.com -o subdomains.txt",
                "explanation": "Subfinder busca subdominios usando múltiples fuentes pasivas."
            },
            {
                "title": "Búsqueda de emails",
                "command": "theHarvester -d example.com -b google,linkedin",
                "explanation": "TheHarvester recopila emails y nombres de múltiples fuentes."
            }
        ],
        "resources": ["https://osintframework.com/"]
    },
    "lab-sqli": {
        "id": "lab-sqli",
        "title": "SQL Injection Práctico",
        "description": "Aprende a explotar vulnerabilidades de inyección SQL.",
        "duration": "60 min",
        "difficulty": "advanced",
        "objectives": [
            "Identificar puntos de inyección",
            "Extraer datos de la base de datos",
            "Usar SQLMap para automatización"
        ],
        "steps": [
            {
                "title": "Detectar SQLi manual",
                "command": "' OR '1'='1",
                "explanation": "Payload básico para probar inyección en formularios de login."
            },
            {
                "title": "SQLMap automático",
                "command": "sqlmap -u 'http://target.com/page?id=1' --dbs",
                "explanation": "SQLMap detecta y explota SQLi automáticamente, listando bases de datos."
            },
            {
                "title": "Extraer tablas",
                "command": "sqlmap -u 'http://target.com/page?id=1' -D database --tables",
                "explanation": "Lista todas las tablas de una base de datos específica."
            }
        ],
        "resources": ["https://owasp.org/www-community/attacks/SQL_Injection"]
    }
}

# ===== NEWS DATA (Static for now, can be enhanced with DDGS later) =====
NEWS_CACHE = {
    "last_update": None,
    "news": []
}

DEFAULT_NEWS = [
    {
        "id": 1,
        "title": "Nueva vulnerabilidad crítica en Apache Log4j 3.0",
        "category": "vulnerabilities",
        "summary_es": "Se ha descubierto una nueva vulnerabilidad de ejecución remota de código en Apache Log4j 3.0 que afecta a millones de aplicaciones Java.",
        "summary_en": "A new remote code execution vulnerability has been discovered in Apache Log4j 3.0 affecting millions of Java applications.",
        "source": "SecurityWeek",
        "date": "2026-01-07",
        "url": "https://securityweek.com"
    },
    {
        "id": 2,
        "title": "Grupo APT compromete infraestructura crítica",
        "category": "breaches",
        "summary_es": "Un grupo de amenazas persistentes avanzadas ha comprometido sistemas de infraestructura crítica en múltiples países europeos.",
        "summary_en": "An advanced persistent threat group has compromised critical infrastructure systems in multiple European countries.",
        "source": "BleepingComputer",
        "date": "2026-01-06",
        "url": "https://bleepingcomputer.com"
    },
    {
        "id": 3,
        "title": "Nueva herramienta de pentesting: NucleiX 4.0",
        "category": "tools",
        "summary_es": "Lanzamiento de NucleiX 4.0 con más de 5000 templates de detección de vulnerabilidades y soporte para fuzzing avanzado.",
        "summary_en": "NucleiX 4.0 released with over 5000 vulnerability detection templates and advanced fuzzing support.",
        "source": "GitHub",
        "date": "2026-01-05",
        "url": "https://github.com/projectdiscovery/nuclei"
    },
    {
        "id": 4,
        "title": "Exploit público para Windows RPC",
        "category": "exploits",
        "summary_es": "Se ha publicado un exploit funcional para la vulnerabilidad CVE-2026-0001 en Windows RPC que permite escalación de privilegios.",
        "summary_en": "A working exploit for CVE-2026-0001 Windows RPC vulnerability has been released, allowing privilege escalation.",
        "source": "ExploitDB",
        "date": "2026-01-04",
        "url": "https://exploit-db.com"
    },
    {
        "id": 5,
        "title": "DEF CON 34 anuncia fechas",
        "category": "events",
        "summary_es": "DEF CON 34 se celebrará en Las Vegas del 7 al 10 de agosto de 2026 con nuevos CTF y villages.",
        "summary_en": "DEF CON 34 will take place in Las Vegas from August 7-10, 2026 with new CTFs and villages.",
        "source": "DEF CON",
        "date": "2026-01-03",
        "url": "https://defcon.org"
    }
]

# ===== EDUCATION ENDPOINTS =====
@education_router.get("/courses")
async def get_courses():
    """Get all available courses"""
    return {"success": True, "courses": COURSES}

@education_router.get("/course/{course_id}")
async def get_course(course_id: str):
    """Get specific course details"""
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        return {"success": False, "error": "Course not found"}
    return {"success": True, "course": course}

@education_router.get("/lab/{lab_id}")
async def get_lab(lab_id: str):
    """Get specific lab details"""
    lab = LABS.get(lab_id)
    if not lab:
        return {"success": False, "error": "Lab not found"}
    return {"success": True, "lab": lab}

@education_router.get("/stats")
async def get_education_stats():
    """Get education platform statistics"""
    total_labs = len(LABS)
    total_courses = len(COURSES)
    return {
        "success": True,
        "stats": {
            "total_courses": total_courses,
            "total_labs": total_labs,
            "total_modules": sum(len(c["modules"]) for c in COURSES)
        }
    }

# ===== NEWS ENDPOINTS =====
@news_router.get("")
async def get_news():
    """Get all news"""
    return {"success": True, "news": DEFAULT_NEWS, "count": len(DEFAULT_NEWS)}

@news_router.get("/category/{category}")
async def get_news_by_category(category: str):
    """Get news filtered by category"""
    filtered = [n for n in DEFAULT_NEWS if n["category"] == category]
    return {"success": True, "news": filtered, "count": len(filtered)}

@news_router.get("/categories")
async def get_categories():
    """Get available news categories"""
    return {
        "success": True,
        "categories": ["vulnerabilities", "exploits", "tools", "breaches", "events"]
    }
