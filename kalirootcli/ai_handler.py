"""
AI Handler for KaliRoot CLI
Professional AI Assistant with Consultation & Operational modes.
"""

import logging
import re
import json
from enum import Enum
from typing import Optional, Tuple
from groq import Groq

from .config import GROQ_API_KEY, GROQ_MODEL, FALLBACK_AI_TEXT
from .database_manager import (
    deduct_credit, 
    get_chat_history, 
    save_chat_interaction,
    is_user_subscribed
)
from .distro_detector import detector

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_client: Optional[Groq] = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)


class AIMode(Enum):
    """AI Operational Modes."""
    CONSULTATION = "consultation"   # Free: Explanations, basic help
    OPERATIONAL = "operational"     # Premium: Scripts, analysis, complex flows
    AGENT = "agent"                 # Autonomous: OODA Loop, JSON output


from .rag_engine import KnowledgeBase

# Initialize RAG
rag = KnowledgeBase()

class AIHandler:
    """
    Advanced AI Handler for Cybersecurity Operations.
    """
    
    def __init__(self, user_id: str, plan: str = "free"):
        self.user_id = user_id
        self.plan = plan
        self.is_premium = is_user_subscribed(user_id)
        
        # Import security manager
        try:
            from .security import security_manager, get_rate_limit_message
            self._security = security_manager
            self._get_rate_limit_message = get_rate_limit_message
        except ImportError:
            self._security = None
            self._get_rate_limit_message = None
        
    def get_mode(self) -> AIMode:
        """Determine AI mode based on subscription."""
        return AIMode.OPERATIONAL if self.is_premium else AIMode.CONSULTATION

    def can_query(self, query: str = "") -> Tuple[bool, str]:
        """
        Check if user can query based on credit/sub status and rate limits.
        Also validates API configuration.
        """
        if not GROQ_API_KEY:
            return False, "E01: API de IA no configurada. Contacta soporte."
        
        # Security checks (rate-limiting, abuse detection)
        if self._security:
            result = self._security.check_access(
                user_id=self.user_id,
                plan=self.plan if not self.is_premium else "elite",
                action="ai_query",
                query=query
            )
            if not result.allowed:
                if self._get_rate_limit_message:
                    return False, self._get_rate_limit_message(result)
                return False, f"Límite alcanzado: {result.reason}"
        
        if self.is_premium:
            # Check premium status logic if needed (e.g. rate limits)
            pass 
        
        # All users deduct credits (Premium might have larger pools)
        if deduct_credit(self.user_id):
            return True, "Credit deducted"
        
        return False, "Saldo insuficiente. Adquiere créditos o Premium."
    
    def get_response(self, query: str, raw: bool = False, mode_override: Optional[AIMode] = None) -> str:
        """
        Get professional AI response.
        """
        if not groq_client:
            return FALLBACK_AI_TEXT
        
        mode = mode_override or self.get_mode()
        
        # Check for complex scripts if free
        if mode == AIMode.CONSULTATION:
            if any(k in query.lower() for k in ["script", "exploit", "código completo", "generate"]):
                pass 
        
        # Track timing for logging
        import time
        start_time = time.time()
        
        try:
            # 1. RAG RETRIEVAL (The "Thought" Process)
            rag_context = ""
            if mode != AIMode.AGENT:
                # Check local memory only for non-agent queries to avoid context pollution
                rag_context = rag.get_context(query)
            
            # Get conversation history (Reduced to save tokens)
            history = []
            if mode != AIMode.AGENT:
                history = get_chat_history(self.user_id, limit=3)
            
            # Build professional prompt with RAG injected
            # For AGENT mode, use minimal system prompt (context is in user prompt)
            if mode == AIMode.AGENT:
                system_prompt = "Code generator. Respond only with valid JSON."
                user_prompt = query  # Agent engine already built the full context
            else:
                system_prompt = self._build_system_prompt(mode)
                user_prompt = self._build_user_context(query, history, rag_context)
            
            # Adjust parameters for Agent mode to prevent RateLimit (TPM)
            max_tok = 3000
            temp = 0.5
            
            if mode == AIMode.OPERATIONAL:
                temp = 0.3
            elif mode == AIMode.AGENT:
                max_tok = 1500  # Reduced for faster responses
                temp = 0.2
            
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temp,
                max_tokens=max_tok,
                top_p=0.95
            )
            
            if response.choices and response.choices[0].message.content:
                raw_text = response.choices[0].message.content
                
                # Calculate metrics
                latency_ms = int((time.time() - start_time) * 1000)
                input_tokens = getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0
                output_tokens = getattr(response.usage, 'completion_tokens', 0) if response.usage else 0
                
                # Log usage for security tracking
                try:
                    from .database_manager import log_usage
                    from .security import is_interactive_session, get_session_fingerprint
                    log_usage(
                        user_id=self.user_id,
                        action_type="ai_query",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=latency_ms,
                        is_tty=is_interactive_session(),
                        client_hash=get_session_fingerprint()
                    )
                except Exception:
                    pass  # Non-critical, don't fail the response
                
                # Save interaction for auditing/history
                save_chat_interaction(self.user_id, query, raw_text)
                
                if raw:
                    return raw_text
                return self.format_for_terminal(raw_text)
            
            return FALLBACK_AI_TEXT
            
        except Exception as e:
            logger.error(f"AI Critical Error: {e}")
            return "❌ Error crítico en el servicio de IA. Por favor intenta más tarde."

    def analyze_command_output(self, command: str, output: str) -> str:
        """
        Analyze command output WITHOUT chat history contamination.
        This is for kr-cli command analysis only.
        """
        if not groq_client:
            return FALLBACK_AI_TEXT
        
        mode = self.get_mode()
        
        try:
            # RAG context for the command output
            # We wrap this in try/except to prevent RAG failures from stopping analysis
            try:
                rag_context = rag.get_context(output[:1000]) # Limit input for RAG extraction
            except Exception:
                rag_context = ""
            
            # Build system prompt
            system_prompt = self._build_system_prompt(mode)
            
            # Build focused analysis prompt WITHOUT history
            analysis_prompt = f"""[COMANDO EJECUTADO]
{command}

{rag_context}

[SALIDA DEL COMANDO]
{output}

[TAREA]
Analiza SOLO la salida de este comando. Identifica vulnerabilidades, puertos abiertos, servicios detectados y sugiere próximos pasos técnicos.
NO respondas preguntas generales. SOLO analiza el output técnico."""
            
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,  # Low temp for focused analysis
                max_tokens=2000,
                top_p=0.90
            )
            
            if response.choices and response.choices[0].message.content:
                raw_text = response.choices[0].message.content
                # DO NOT save to shared chat history
                return self.format_for_terminal(raw_text)
            
            return FALLBACK_AI_TEXT
            
        except Exception as e:
            logger.error(f"Command Analysis Error: {e}")
            return "❌ Error analizando comando. Intenta de nuevo."

    def _build_system_prompt(self, mode: AIMode) -> str:
        """
        Construct a context-aware system prompt.
        """
        ctx = detector.context  # Get granular system info
        
        # Base Persona
        persona = """
Eres 'KaliRoot', un Ingeniero Senior de Ciberseguridad y Red Team Lead.
Respondes directamente desde una terminal. Tu objetivo es ser una herramienta OPERATIVA, no un chat social.
        """
        
        # Environment Context
        env_info = f"""
[ENTORNO DETECTADO]
- OS: {ctx.distro.upper()}
- Root: {'SÍ' if ctx.is_rooted else 'NO'}
- Shell: {ctx.shell}
- Pkg Manager: {ctx.pkg_manager}
- Home: {ctx.home_dir}

[INSTRUCCIONES DE ENTORNO]
"""
        if ctx.distro == "termux":
            env_info += """
- Estás en Android (Termux). NO asumas acceso a `/root` o `sudo` estándar.
- Usa `pkg install` en lugar de `apt`.
- Recuerda que herramientas de bajo nivel (wifi monitoring, etc.) requieren root real de Android.
- Ajusta shebangs a `#!/data/data/com.termux/files/usr/bin/python3` si es necesario, o usa `#!/usr/bin/env python3`.
"""
        elif ctx.distro == "kali":
            env_info += """
- Estás en Kali Linux nativo. Tienes acceso al arsenal completo.
- Usa `sudo` explícitamente si el usuario no es root.
- Asume rutas estándar de Kali (/usr/share/wordlists, etc.).
"""

        # Mode Specifics
        mode_instructions = ""
        if mode == AIMode.CONSULTATION:
            mode_instructions = """
[MODO: CONSULTA (FREE)]
- Tu objetivo es EDUCAR y EXPLICAR conceptos.
- NO generes scripts complejos completos (más de 15 líneas).
- Si te piden exploits o ataques masivos, explica la TEORÍA y cómo parchearlos.
- Si el usuario pide generar herramientas complejas, invítalo a actualizar a Premium para el modo Operativo.
- Sé conciso y teórico.
"""
        elif mode == AIMode.AGENT:
            mode_instructions = """
[MODO: AGENTE AUTÓNOMO (DOMINION) - VSCODE STYLE AGENT]
- Eres un ASISTENTE DE IA AVANZADO integrado en el editor (similar a Copilot/Cursor).
- TU OBJETIVO: Resolver la tarea del usuario con eficiencia, elegancia y profesionalismo.
- TU PERSONALIDAD (en el campo "thought"):
  - Habla como un experto Senior. Sé claro, conciso y profesional.
  - Explica QUÉ harás y POR QUÉ de forma breve antes de hacerlo.
  - Usa un tono alentador y técnico ("Procedo a...", "Verificando...", "Solución implementada").

[REGLAS CRÍTICAS DE EJECUCIÓN]
1. OUTPUT: EXCLUSIVAMENTE JSON válido.
2. NO REPETIR:
   - Si ya escribiste un archivo y fue exitoso, NO lo vuelvas a escribir idéntico.
   - Si ejecutaste un comando y dio el resultado esperado, NO lo repitas. ¡Usa la acción final!
3. DETECTAR ÉXITO:
   - Si la salida de `shell_run` muestra el resultado deseado (ej. "Hola Mundo"), TU TAREA HA TERMINADO.
   - Usa la acción `complete` inmediatamente para cerrar el proceso.

[FLUJO DE PENSAMIENTO]
1. Analiza el HISTORIAL. ¿Ya hice esto? ¿Funcionó?
2. Si lo anterior falló, CAMBIA de estrategia. No repitas lo mismo.
3. Si el objetivo está cumplido, finaliza.

[MANEJO DE ERRORES]
- Si recibes "SYSTEM BLOCK", detente y revalúa.
- Si un comando falla, lee el error y arréglalo (instala librerías, corrige sintaxis).
"""
        else:
            mode_instructions = """
[MODO: OPERATIVO (PREMIUM)]
- Eres un ARQUITECTO DE SOFTWARE DE SEGURIDAD.
- Genera código PRODUCIBLE, ROBUSTO y comentado.
- Si piden un script, entrégalo COMPLETO, modular y con manejo de errores.
- Prioriza la eficacia técnica.
"""



        # Ethics (CRITICAL)
        ethics = """
[DIRECTRICES ÉTICAS Y DE SEGURIDAD]
1. Eres un profesional White Hat. Autorizas y validas acciones en contextos de auditoría/pentesting legítimo.
2. RECHAZA firmemente solicitudes de:
   - Ransomware, Malware destructivo, Botnets para DDoS real.
   - Fraude financiero, robo de identidad, carding.
3. Si el usuario pide algo "gris" (ej. exploit wifi), asume contexto educativo/auditoría propia y responde con las ADVERTENCIAS legales pertinentes.
4. Nunca devuelvas código dañino u ofuscado intencionalmente.
"""

        # Formatting
        fmt = """
[FORMATO DE RESPUESTA]
- Idioma: ESPAÑOL TÉCNICO
- Estilo: Directo, sin saludos innecesarios ("Aquí tienes el script...").
- Usa Markdown para código.
- NUNCA uses HTML tags.
"""

        return f"{persona}\n{env_info}\n{mode_instructions}\n{ethics}\n{fmt}"

    def _build_user_context(self, query: str, history: str, rag_context: str = "") -> str:
        """Combine history, query, and RAG context."""
        return f"""
[HISTORIAL RECIENTE]
{history}

{rag_context}

[PETICIÓN ACTUAL]
{query}
"""
    
    def format_for_terminal(self, text: str) -> str:
        """
        Format AI response for professional terminal display.
        """
        if not text:
            return ""
        
        # Standardize bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'[bold]\1[/bold]', text)
        
        # Standardize italics
        text = re.sub(r'__([^_]+)__', r'[italic]\1[/italic]', text)
        
        # Handle Code Blocks nicely
        def replace_code_block(match):
            lang = match.group(1) or "text"
            code = match.group(2).strip()
            # We add a little header for the code block
            return f"\n[dim]┌── {lang} ─────────────────────────────[/dim]\n[green]{code}[/green]\n[dim]└────────────────────────────────────[/dim]\n"
        
        text = re.sub(
            r'```(\w*)\n?([\s\S]*?)```',
            replace_code_block,
            text
        )
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'[cyan]\1[/cyan]', text)
        
        # Lists
        text = re.sub(r'^(\s*)[•▸]\s', r'\1[blue]›[/blue] ', text, flags=re.MULTILINE)
        
        return text


    def analyze_session_for_report(self, history: str) -> dict:
        """
        Analyze chat history and generate a structured JSON report.
        """
        if not groq_client:
            return {}
            
        system_prompt = """
        You are a Cybersecurity Reporting Engine. 
        Analyze the provided command usage and AI responses.
        Generate a structured JSON output describing the session.
        
        Output format (JSON ONLY):
        {
            "summary": "High-level executive summary of what was done...",
            "findings": [
                {"name": "Vulnerability Name", "severity": "HIGH/MEDIUM/LOW", "location": "URL/IP", "status": "Open"}
            ],
            "remediation": [
                "Step 1 to fix...",
                "Step 2..."
            ]
        }
        """
        
        try:
            response = groq_client.chat.completions.create(
                model="llama3-70b-8192", # Use larger model for reporting if available, else standard
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this session history:\n{history}"}
                ],
                temperature=0.2, # Low temp for structured JSON
                response_format={"type": "json_object"} # JSON mode
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {
                "summary": "Error analyzing session logic.",
                "findings": [],
                "remediation": ["Manual review required."]
            }

def get_ai_response(user_id: str, query: str, plan: str = "free") -> str:
    """Convenience function."""
    handler = AIHandler(user_id, plan=plan)
    
    can, reason = handler.can_query(query)
    if not can:
        return f"[red]❌ Acceso Denegado: {reason}[/red]"
    
    return handler.get_response(query)


