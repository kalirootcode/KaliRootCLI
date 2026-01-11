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

# ===== AI COURSES ENDPOINTS =====
import os
import re
import json
import httpx
import time
from pydantic import BaseModel
from typing import Optional

# Supabase client for AI courses
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class CourseGenerationRequest(BaseModel):
    url: str

def generate_slug(title: str) -> str:
    """Generate URL-safe slug from title"""
    slug = title.lower()
    slug = re.sub(r'[áàäâ]', 'a', slug)
    slug = re.sub(r'[éèëê]', 'e', slug)
    slug = re.sub(r'[íìïî]', 'i', slug)
    slug = re.sub(r'[óòöô]', 'o', slug)
    slug = re.sub(r'[úùüû]', 'u', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')[:80]

async def fetch_web_content(url: str) -> str:
    """Fetch and extract text content from a URL"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Basic HTML to text extraction
            html = response.text
            # Remove scripts and styles
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove tags but keep text
            text = re.sub(r'<[^>]+>', ' ', html)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text)
            return text[:15000]  # Limit content
    except Exception as e:
        return f"Could not fetch content: {str(e)}"

async def generate_course_with_ai(url: str, content: str) -> dict:
    """Use Gemini AI to generate a professional course"""
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not configured"}
    
    prompt = f"""Eres un experto en ciberseguridad y hacking ético. Vas a crear un curso profesional e interactivo basado en la siguiente herramienta/recurso.

URL: {url}
Contenido extraído:
{content[:10000]}

CREA un curso profesional con las siguientes características:
1. TÍTULO: Un título viral y atractivo que genere retención (máx 60 caracteres)
2. DESCRIPCIÓN: Descripción profesional del curso (2-3 oraciones)
3. DIFICULTAD: beginner, intermediate, advanced, o expert
4. ICONO: Un emoji representativo de la herramienta
5. DURACIÓN: Estimación (ej: "3-5 horas")

6. CONTENIDO con esta estructura JSON:
{{
  "intro": "Introducción profunda al tema con contexto hacker (2-3 párrafos)",
  "objectives": ["Objetivo 1", "Objetivo 2", "Objetivo 3", "Objetivo 4"],
  "modules": [
    {{
      "id": "modulo-1",
      "title": "Título del Módulo",
      "sections": [
        {{
          "title": "Título de la Sección",
          "theory": "Teoría profunda y profesional explicando conceptos (mín 200 palabras)",
          "commands": [
            {{"command": "comando ejemplo", "explanation": "Explicación detallada de lo que hace"}}
          ],
          "tips": ["Tip profesional 1", "Tip profesional 2"]
        }}
      ]
    }}
  ],
  "resources": [{{"title": "Recurso", "url": "https://..."}}],
  "conclusion": "Conclusión y próximos pasos (1 párrafo)"
}}

REGLAS IMPORTANTES:
- Incluye comandos REALES y funcionales desde básicos hasta avanzados
- La teoría debe ser profunda y técnica, estilo documentación profesional
- Incluye al menos 3 módulos con 2-3 secciones cada uno
- Los comandos deben ir del más básico al más complejo progresivamente
- Estilo hacker pero educativo y profesional
- Sin censura pero con ética (menciona siempre uso responsable)
- Incluye ejemplos prácticos reales

Responde SOLO con un JSON válido con esta estructura:
{{
  "title": "...",
  "description": "...",
  "difficulty": "...",
  "icon": "...",
  "duration": "...",
  "content": {{ ... }}
}}"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.8,
                        "maxOutputTokens": 8192
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract text from response
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                course_data = json.loads(json_match.group())
                return course_data
            else:
                return {"error": "Could not parse AI response"}
                
    except Exception as e:
        return {"error": f"AI generation failed: {str(e)}"}

@education_router.post("/admin/generate-course/{link_id}")
async def generate_course(link_id: str):
    """Generate a course from a URL using AI"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"success": False, "error": "Database not configured"}
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Get the course link
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/course_links?id=eq.{link_id}&select=*",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            links = response.json()
            
            if not links:
                return {"success": False, "error": "Link not found"}
            
            link = links[0]
            url = link["url"]
            
            # Update status to generating
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/course_links?id=eq.{link_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={"status": "generating"}
            )
            
            # Fetch web content
            content = await fetch_web_content(url)
            
            # Generate course with AI
            course_data = await generate_course_with_ai(url, content)
            
            if "error" in course_data:
                # Update link with error
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/course_links?id=eq.{link_id}",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"status": "error", "error_message": course_data["error"]}
                )
                return {"success": False, "error": course_data["error"]}
            
            # Generate slug
            slug = generate_slug(course_data.get("title", "curso"))
            # Make unique by adding timestamp if needed
            slug = f"{slug}-{int(time.time()) % 10000}"
            
            generation_time = int((time.time() - start_time) * 1000)
            
            # Save course to database
            course_insert = {
                "link_id": link_id,
                "title": course_data.get("title", "Curso sin título"),
                "slug": slug,
                "description": course_data.get("description", ""),
                "icon": course_data.get("icon", "📚"),
                "difficulty": course_data.get("difficulty", "intermediate"),
                "duration": course_data.get("duration", "2-4 horas"),
                "content": course_data.get("content", {}),
                "is_published": False,
                "generation_time_ms": generation_time
            }
            
            insert_response = await client.post(
                f"{SUPABASE_URL}/rest/v1/ai_courses",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                json=course_insert
            )
            
            if insert_response.status_code >= 400:
                raise Exception(f"Insert failed: {insert_response.text}")
            
            # Update link status to completed
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/course_links?id=eq.{link_id}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={"status": "completed", "title": course_data.get("title")}
            )
            
            return {
                "success": True,
                "course": course_insert,
                "generation_time_ms": generation_time
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@education_router.get("/ai-courses")
async def get_published_ai_courses():
    """Get all published AI-generated courses"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"success": False, "error": "Database not configured", "courses": []}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/ai_courses?is_published=eq.true&select=id,title,slug,description,icon,difficulty,duration,total_views,created_at",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            courses = response.json()
            return {"success": True, "courses": courses, "count": len(courses)}
    except Exception as e:
        return {"success": False, "error": str(e), "courses": []}

@education_router.get("/ai-course/{slug}")
async def get_ai_course_by_slug(slug: str):
    """Get a single AI course by slug"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"success": False, "error": "Database not configured"}
    
    try:
        async with httpx.AsyncClient() as client:
            # Get course
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/ai_courses?slug=eq.{slug}&is_published=eq.true&select=*",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            courses = response.json()
            
            if not courses:
                return {"success": False, "error": "Course not found"}
            
            course = courses[0]
            
            # Increment view count
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/ai_courses?id=eq.{course['id']}",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={"total_views": course.get("total_views", 0) + 1}
            )
            
            return {"success": True, "course": course}
    except Exception as e:
        return {"success": False, "error": str(e)}
