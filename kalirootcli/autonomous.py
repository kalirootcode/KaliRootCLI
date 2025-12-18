"""
Autonomous Security Agent Module
Implements OODA Loop (Observe, Orient, Decide, Act) for semi-autonomous operations.
"""

import sys
import logging
from typing import List, Dict, Any
from .ai_handler import get_ai_response
from .ui.display import console, print_info, print_success, print_error, show_loading, Panel
from .distro_detector import detector

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """Advanced Semi-Autonomous Security Agent with DOMINION logic."""
    
    def __init__(self, target: str, user_id: str = "anonymous"):
        self.target = target
        self.user_id = user_id
        self.history: List[str] = []
        self.max_steps = 10
        self.current_step = 0
        self.distro = detector.distro
        
    def run_loop(self):
        """Execute the advanced OODA loop."""
        print_info(f"🚀 Iniciando Agente DOMINION sobre: {self.target}")
        print_info(f"💻 Entorno detectado: {self.distro}")
        
        # Bridge to DominionAgent for complex, persistent tasks
        # But keep this loop for quick terminal-based operations
        while self.current_step < self.max_steps:
            self.current_step += 1
            console.rule(f"[bold cyan]OODA Step {self.current_step}/{self.max_steps}[/bold cyan]")
            
            # 1. OBSERVE & ORIENT
            context = "\n".join(self.history[-3:]) if self.history else "Inicio de operación."
            
            prompt = f"""
            ENTORNO: {self.distro}
            OBJETIVO: Realizar auditoría/operación sobre {self.target}
            HISTORIAL RECIENTE: {context}
            
            Como experto en ciberseguridad, decide el siguiente comando EXACTO a ejecutar.
            Si necesitas buscar información, sugiere una búsqueda.
            Si el objetivo está cumplido, responde 'DONE'.
            Retorna SOLO el comando o 'DONE'.
            """
            
            with show_loading("🤖 Analizando siguiente movimiento..."):
                response = get_ai_response(self.user_id, prompt)
                next_command = self._clean_command(response)
            
            if "DONE" in next_command.upper() or not next_command:
                print_success("✅ Agente completó sus objetivos.")
                break
                
            console.print(f"[bold yellow]👉 Sugerencia:[/bold yellow] {next_command}")
            
            # 2. DECIDE
            action = console.input("[bold green]¿Ejecutar? (s/n/q/edit): [/bold green]").lower()
            
            if action == 'q':
                break
            elif action == 'edit':
                next_command = console.input("[bold cyan]Nuevo comando: [/bold cyan]")
            elif action != 's':
                print_info("Acción omitida.")
                continue
                
            # 3. ACT
            try:
                import subprocess
                
                # Platform specific adjustments
                cmd_to_run = next_command
                if "linux" in self.distro.lower() and "sudo " not in cmd_to_run:
                    # Optional: AI could decide if sudo is needed, but we let it as provided
                    pass

                with show_loading(f"⚡ Ejecutando: {cmd_to_run}..."):
                    process = subprocess.run(
                        cmd_to_run, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=120
                    )
                    
                output = (process.stdout + process.stderr)
                # Success/Failure feedback
                if process.returncode == 0:
                    print_success(f"Comando ejecutado (RC: 0)")
                else:
                    print_error(f"Comando falló (RC: {process.returncode})")

                # Truncate output for history but keep key info
                obs_text = output[:2000] if len(output) > 2000 else output
                self.history.append(f"CMD: {cmd_to_run}\nOUT: {obs_text}")
                
                # Display output
                from rich.syntax import Syntax
                if output.strip():
                    console.print(Panel(output.strip()[:1000], title="Salida de Terminal", border_style="dim"))
                
            except Exception as e:
                print_error(f"Error ejecución: {e}")
                self.history.append(f"CMD: {next_command}\nERR: {str(e)}")
                
    def _clean_command(self, text: str) -> str:
        """Extract command from AI response."""
        import re
        # Remove rich tags if any
        text = re.sub(r'\[.*?\]', '', text)
        # Remove markdown code blocks
        text = text.replace("```bash", "").replace("```", "").strip()
        lines = text.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(("#", "Acceso Denegado")):
                return line.strip()
        return "DONE"

def run_autonomous_mode(target: str, user_id: str = "00000000-0000-0000-0000-000000000000"):
    # Ensure user_id is a valid UUID string
    valid_user_id = user_id
    if user_id in ["anonymous", "cli_user", "default"]:
        valid_user_id = "00000000-0000-0000-0000-000000000000"
        
    agent = AutonomousAgent(target, valid_user_id)
    agent.run_loop()
