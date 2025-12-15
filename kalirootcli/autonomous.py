"""
Autonomous Security Agent Module
Implements OODA Loop (Observe, Orient, Decide, Act) for semi-autonomous operations.
"""

import sys
import logging
from typing import List, Dict, Any
from .ai_handler import get_ai_response
from .ui.display import console, print_info, print_success, print_error, show_loading

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """Semi-Autonomous Security Agent."""
    
    def __init__(self, target: str):
        self.target = target
        self.history: List[str] = []
        self.max_steps = 5
        self.current_step = 0
        
    def run_loop(self):
        """Execute the OODA loop."""
        print_info(f"🚀 Iniciando Agente Autónomo sobre: {self.target}")
        
        while self.current_step < self.max_steps:
            self.current_step += 1
            console.rule(f"[bold cyan]Step {self.current_step}/{self.max_steps}[/bold cyan]")
            
            # 1. OBSERVE & ORIENT (What do we know?)
            context = "\n".join(self.history) if self.history else "No actions taken yet."
            
            prompt = f"""
            CTX: Target is {self.target}.
            History: {context}
            
            DECIDE: What is the SINGLE best next command to run? 
            Return ONLY the command string.
            If done, return 'DONE'.
            """
            
            with show_loading("🤖 Thinking (Deciding next move)..."):
                # Use AI to decide next step
                # We strip to get just the command
                response = get_ai_response("autonomous_agent", prompt)
                next_command = self._clean_command(response)
            
            if "DONE" in next_command or not next_command:
                print_success("✅ Agente decidió terminar la operación.")
                break
                
            console.print(f"[bold yellow]👉 Propuesta:[/bold yellow] {next_command}")
            
            # 2. DECIDE (Human authorization in loop)
            # For semi-autonomous safety, we request confirmation
            action = console.input("[bold green]¿Ejecutar? (s/n/q): [/bold green]").lower()
            
            if action == 'q':
                break
            elif action != 's':
                print_info("Acción omitida.")
                continue
                
            # 3. ACT
            try:
                import subprocess
                CMD = next_command.split()
                
                with show_loading(f"⚡ Ejecutando: {next_command}..."):
                    result = subprocess.run(CMD, capture_output=True, text=True, timeout=60)
                    
                output = (result.stdout + result.stderr)[:1000] # Truncate for memory
                self.history.append(f"CMD: {next_command}\nOUT: {output}")
                
                console.print(f"[dim]{output.strip()}[/dim]")
                
            except Exception as e:
                print_error(f"Error ejecución: {e}")
                self.history.append(f"CMD: {next_command}\nERR: {str(e)}")
                
    def _clean_command(self, text: str) -> str:
        """Extract command from AI response."""
        # Remove markdown code blocks if present
        text = text.replace("```bash", "").replace("```", "").strip()
        lines = text.split('\n')
        # Return first non-empty line
        for line in lines:
            if line.strip() and not line.startswith("#"):
                return line.strip()
        return "DONE"

def run_autonomous_mode(target: str):
    agent = AutonomousAgent(target)
    agent.run_loop()
