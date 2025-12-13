"""
AI Handler for KaliRoot CLI
Professional AI Assistant with Consultation & Operational modes.
"""

import logging
import re
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


class AIHandler:
    """
    Advanced AI Handler for Cybersecurity Operations.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.is_premium = is_user_subscribed(user_id)
        
    def get_mode(self) -> AIMode:
        """Determine AI mode based on subscription."""
        return AIMode.OPERATIONAL if self.is_premium else AIMode.CONSULTATION

    def can_query(self) -> Tuple[bool, str]:
        """
        Check if user can query based on credit/sub status.
        Also validates API configuration.
        """
        if not GROQ_API_KEY:
            return False, "E01: API de IA no configurada. Contacta soporte."
        
        if self.is_premium:
            return True, "Premium Access"
        
        # Free users deduct credits
        if deduct_credit(self.user_id):
            return True, "Credit deducted"
        
        return False, "Saldo insuficiente. Adquiere créditos o Premium."
    
    def get_response(self, query: str) -> str:
        """
        Get professional AI response.
        
        Args:
            query: User's technical query or command request
            
        Returns:
            Formatted response string
        """
        if not groq_client:
            return FALLBACK_AI_TEXT
        
        mode = self.get_mode()
        
        # Check if free user is trying to generate complex scripts (basic keyword check)
        # Ideally this would be handled by the AI prompting, but we can do a quick check
        if mode == AIMode.CONSULTATION:
            if any(k in query.lower() for k in ["script", "exploit", "código completo", "generate"]):
                # We don't block it, but the AI prompt will be strictly "consultation"
                pass 
        
        try:
            # Get conversation history
            history = get_chat_history(self.user_id, limit=6)
            
            # Build professional prompt
            system_prompt = self._build_system_prompt(mode)
            user_prompt = self._build_user_context(query, history)
            
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3 if mode == AIMode.OPERATIONAL else 0.5, # More precise for scripts
                max_tokens=3000,
                top_p=0.95
            )
            
            if response.choices and response.choices[0].message.content:
                raw_text = response.choices[0].message.content
                
                # Save interaction for auditing/history
                save_chat_interaction(self.user_id, query, raw_text)
                
                return self.format_for_terminal(raw_text)
            
            return FALLBACK_AI_TEXT
            
        except Exception as e:
            logger.error(f"AI Critical Error: {e}")
            return "❌ Error crítico en el servicio de IA. Por favor intenta más tarde."

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

    def _build_user_context(self, query: str, history: str) -> str:
        """Combine history and query."""
        return f"""
[HISTORIAL RECIENTE]
{history}

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


def get_ai_response(user_id: str, query: str) -> str:
    """Convenience function."""
    handler = AIHandler(user_id)
    
    can, reason = handler.can_query()
    if not can:
        return f"[red]❌ Acceso Denegado: {reason}[/red]"
    
    return handler.get_response(query)

