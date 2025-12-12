"""
AI Handler for KaliRoot CLI
Handles Groq AI integration and response formatting for terminal.
"""

import logging
import re
from typing import Optional
from groq import Groq

from .config import GROQ_API_KEY, GROQ_MODEL, FALLBACK_AI_TEXT
from .database_manager import (
    deduct_credit, 
    get_chat_history, 
    save_chat_interaction,
    is_user_subscribed
)

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_client: Optional[Groq] = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)


class AIHandler:
    """Handles AI responses from Groq."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def can_query(self) -> tuple[bool, str]:
        """
        Check if user can make AI query.
        
        Returns:
            (can_query, reason)
        """
        if not GROQ_API_KEY:
            return False, "API de IA no configurada"
        
        # Check credits or subscription
        if is_user_subscribed(self.user_id):
            return True, "Premium"
        
        # Try to deduct credit
        if deduct_credit(self.user_id):
            return True, "Credit deducted"
        
        return False, "Sin créditos disponibles"
    
    def get_response(self, query: str) -> str:
        """
        Get AI response for a query.
        
        Args:
            query: User's question
        
        Returns:
            AI response string
        """
        if not groq_client:
            return FALLBACK_AI_TEXT
        
        # Get chat history for context
        history = get_chat_history(self.user_id, limit=6)
        
        # Build the prompt
        prompt = self._build_prompt(query, history)
        
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=2500,
                top_p=0.95
            )
            
            if response.choices and response.choices[0].message.content:
                raw_text = response.choices[0].message.content
                
                # Save interaction
                save_chat_interaction(self.user_id, query, raw_text)
                
                # Format for terminal
                return self.format_for_terminal(raw_text)
            
            return FALLBACK_AI_TEXT
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return FALLBACK_AI_TEXT
    
    def _build_prompt(self, query: str, history: str) -> str:
        """Build the AI prompt."""
        return f"""=== CONFIGURACIÓN OBLIGATORIA ===
⚠️ IDIOMA: Responde SIEMPRE y ÚNICAMENTE en ESPAÑOL.
⚠️ NO traduzcas. NO des la respuesta primero en inglés.
⚠️ Si la información está en inglés, tradúcela al español.

=== IDENTIDAD ===
Soy 'KaliRoot' 💀 - Mente Hacker Elite especializada en Ciberseguridad Ofensiva.
▸ Nivel: Red Team Senior / Pentester / Security Researcher
▸ Estilo: Técnico, directo, sin rodeos
▸ Filosofía: El conocimiento debe ser libre 🔓
▸ Entorno: Respondiendo desde terminal CLI (Termux/Kali Linux)

=== FORMATO DE RESPUESTA ===
1. **ESTRUCTURA CLARA**:
   • Usa saltos de línea para separar secciones
   • Crea listas con bullets (▸ ◉ ➤ •)
   • Títulos cortos con emojis relevantes

2. **EMOJIS ESTRATÉGICOS** (usa variedad):
   💀 🔓 🛡️ ⚡ 🔥 💻 🖥️ 📡 🌐 🔍 🗝️ ⚙️ 🎯 📌 ✅ ❌ ⚠️

3. **CÓDIGO Y COMANDOS**:
   • Usa bloques de código con triple backtick
   • Incluye comentarios explicativos
   • Código funcional y probado

4. **ESTILO DE ESCRITURA**:
   • Frases cortas y directas
   • Explicaciones paso a paso
   • Resalta términos técnicos con **negrita**
   • Conciso pero completo

5. **TEMAS QUE DOMINO**:
   Pentesting, Exploits, Reverse Engineering, OSINT,
   Wireless Hacking, Web Security, Network Security,
   Malware Analysis, Criptografía, Social Engineering,
   Kali Linux, Termux, Python, Bash, CTF

=== HISTORIAL ===
{history}

=== PREGUNTA ===
{query}

Responde en ESPAÑOL de forma clara, técnica y profesional:"""
    
    def format_for_terminal(self, text: str) -> str:
        """
        Format AI response for terminal display.
        Uses Rich markup for formatting.
        
        Args:
            text: Raw AI response
        
        Returns:
            Formatted text for terminal
        """
        if not text:
            return ""
        
        # Replace markdown bold with Rich markup
        text = re.sub(r'\*\*([^*]+)\*\*', r'[bold]\1[/bold]', text)
        
        # Replace markdown italic
        text = re.sub(r'__([^_]+)__', r'[italic]\1[/italic]', text)
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'[italic]\1[/italic]', text)
        
        # Handle code blocks - convert to Rich Syntax format
        # For simple display, we'll just style them
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2).strip()
            return f"\n[dim]{'─' * 40}[/dim]\n[green]{code}[/green]\n[dim]{'─' * 40}[/dim]\n"
        
        text = re.sub(
            r'```(\w*)\n?([\s\S]*?)```',
            replace_code_block,
            text
        )
        
        # Handle inline code
        text = re.sub(r'`([^`]+)`', r'[cyan]\1[/cyan]', text)
        
        # Style bullet points
        text = re.sub(r'^(\s*)[•▸◉➤]\s', r'\1[cyan]▸[/cyan] ', text, flags=re.MULTILINE)
        text = re.sub(r'^(\s*)-\s', r'\1[cyan]▸[/cyan] ', text, flags=re.MULTILINE)
        text = re.sub(r'^(\s*)\*\s', r'\1[cyan]▸[/cyan] ', text, flags=re.MULTILINE)
        
        # Style numbered lists
        text = re.sub(r'^(\d+)\.\s', r'[yellow]\1.[/yellow] ', text, flags=re.MULTILINE)
        
        return text


def get_ai_response(user_id: str, query: str) -> str:
    """Convenience function to get AI response."""
    handler = AIHandler(user_id)
    
    can_query, reason = handler.can_query()
    
    if not can_query:
        if "créditos" in reason.lower():
            return "[red]❌ Sin créditos disponibles.[/red]\n\nUsa [cyan]'comprar'[/cyan] para obtener más créditos o suscríbete a Premium."
        return f"[red]❌ {reason}[/red]"
    
    return handler.get_response(query)
