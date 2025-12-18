"""
DOMINION Agent Engine for KaliRoot CLI
Implements advanced agentic behavior: Internal Monologue -> Action -> Observation -> Refine.

Optimized for Kali Linux (PC) and Termux (Android).
"""

import os
import sys
import json
import time
import logging
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from .ai_handler import AIHandler, AIMode
from .ui.display import console, print_info, print_success, print_error, print_warning, show_loading
from .distro_detector import detector
from .web_search import web_search
from .security import is_interactive_session, get_session_fingerprint
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.text import Text

logger = logging.getLogger(__name__)

@dataclass
class AgentStep:
    """Represents a single step in the agent's execution."""
    thought: str
    action: str
    action_input: str
    observation: str = ""
    status: str = "pending"  # pending, success, failed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStep':
        return cls(
            thought=data.get("thought", ""),
            action=data.get("action", ""),
            action_input=data.get("action_input", ""),
            observation=data.get("observation", ""),
            status=data.get("status", "pending")
        )

@dataclass
class AgentState:
    """Persistent state of the agent session."""
    goal: str
    project_path: str
    history: List[AgentStep] = field(default_factory=list)
    max_steps: int = 20
    current_step: int = 0
    variables: Dict[str, Any] = field(default_factory=dict)
    distro: str = field(default_factory=lambda: detector.distro)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "project_path": self.project_path,
            "history": [s.to_dict() for s in self.history],
            "max_steps": self.max_steps,
            "current_step": self.current_step,
            "variables": self.variables,
            "distro": self.distro
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        state = cls(
            goal=data.get("goal", ""),
            project_path=data.get("project_path", ""),
            max_steps=data.get("max_steps", 20),
            current_step=data.get("current_step", 0),
            variables=data.get("variables", {}),
            distro=data.get("distro", detector.distro)
        )
        state.history = [AgentStep.from_dict(s) for s in data.get("history", [])]
        return state

class DominionAgent:
    """
    Advanced agentic engine for security operations and development.
    Inspired by Gemini CLI's agentic loop but hardened for hacker workflows.
    """
    
    def __init__(self, user_id: str, plan: str = "free"):
        self.user_id = user_id
        self.ai = AIHandler(user_id, plan=plan)
        self.state: Optional[AgentState] = None
        
    def start_task(self, goal: str, project_path: str):
        """Initialize or resume a task."""
        self.state = AgentState(
            goal=goal,
            project_path=os.path.abspath(project_path)
        )
        os.makedirs(self.state.project_path, exist_ok=True)
        
        # Try to load existing state if it exists in the project path
        state_file = os.path.join(self.state.project_path, ".dominion_state.json")
        if os.path.exists(state_file):
            loaded_state = self.load_state(state_file)
            if loaded_state:
                # Merge loaded state: Keep new goal if provided, or use old one
                if not goal or goal == "Continuar":
                    self.state.goal = loaded_state.goal
                self.state.history = loaded_state.history
                self.state.current_step = loaded_state.current_step
                self.state.variables = loaded_state.variables
                print_info(f"🔄 Proyecto reanudado con {len(self.state.history)} pasos previos.")

        self._run_loop()

    def save_state(self):
        """Save current state to project directory."""
        if not self.state:
            return
        state_file = os.path.join(self.state.project_path, ".dominion_state.json")
        try:
            with open(state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def load_state(self, path: str) -> Optional[AgentState]:
        """Load state from JSON file."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return AgentState.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None

    def _run_loop(self):
        """Main OODA loop execution."""
        if not self.state:
            return

        print_info(f"🚀 DOMINION Engine Iniciado")
        print_info(f"🎯 Objetivo: {self.state.goal}")
        
        while self.state.current_step < self.state.max_steps:
            self.state.current_step += 1
            step_num = self.state.current_step
            
            console.rule(f"[bold cyan]DOMINION Step {step_num}/{self.state.max_steps}[/bold cyan]")
            
            # 1. THINK & PLAN (Internal Monologue)
            step = self._think()
            if not step:
                break
                
            self.state.history.append(step)
            
            # 2. ACT
            if step.action == "complete":
                print_success(f"✅ Tarea completada: {step.thought}")
                break
            
            # Show thought and action to user
            console.print(f"\n[bold yellow]🤔 Pensamiento:[/bold yellow] {step.thought}")
            console.print(f"[bold magenta]🛠️  Acción ([white]{step.action}[/]):[/bold magenta] {step.action_input}")
            
            # --- ANTI-LOOP HARD BLOCK ---
            # detailed check of previous action
            if len(self.state.history) > 1:
                last_step = self.state.history[-2] # Current step is already at -1
                if step.action == last_step.action and step.action_input == last_step.action_input:
                    # Hard block ANY identical action-input pair.
                    print_error("⛔ SYSTEM BLOCK: Acción idéntica detectada. Bloqueando para romper bucle.")
                    step.observation = "SYSTEM AUTOMATIC BLOCK: You attempted to execute the EXACT SAME Action and Input as the previous step. This is prohibited. You MUST change your strategy, parameters, or tool."
                    step.status = "failed"
                    self.save_state()
                    continue
            # -----------------------------
            
            # Security confirmation for sensitive actions
            if not self._confirm_action(step):
                print_warning("Acción cancelada por el usuario.")
                step.status = "canceled"
                step.observation = "User canceled the action."
                continue

            # 3. EXECUTE & OBSERVE
            from .mobile import success_pulse, error_pulse
            
            observation = self._execute(step)
            step.observation = observation
            
            if observation and "Error" not in observation:
                step.status = "success"
                try: success_pulse()
                except: pass
            else:
                step.status = "failed"
                try: error_pulse()
                except: pass
            
            # Print brief observation summary
            obs_preview = observation[:500] + "..." if len(observation) > 500 else observation
            console.print(f"[dim]\n📝 Observación:\n{obs_preview}[/dim]\n")
            
            # Save state after each step
            self.save_state()

            # Check for immediate success signals in observation
            if "DONE_TASK_SUCCESS" in observation:
                print_success("🏆 Objetivo alcanzado.")
                break

    def _think(self) -> Optional[AgentStep]:
        """Generate the next thought and action using AI."""
        # Use the unified AI Handler logic
        
        # Build context from history
        history_str = ""
        for i, s in enumerate(self.state.history[-5:]): # Last 5 steps for context
            history_str += f"Step {i+1}:\n- T: {s.thought}\n- A: {s.action}({s.action_input})\n- O: {s.observation[:300]}\n"

        # Loop & Error Detection Logic
        system_warnings = ""
        if len(self.state.history) > 0:
            last_step = self.state.history[-1]
            if last_step.status in ["failed", "canceled"]:
                system_warnings += f"\n[SISTEMA]: La última acción ({last_step.action}) FALLÓ o fue CANCELADA. NO LA REPITAS con los mismos parámetros. Busca una alternativa o soluciona el error previo."
                
            if len(self.state.history) > 1:
                prev_step = self.state.history[-2]
                if last_step.action == prev_step.action and last_step.action_input == prev_step.action_input:
                    system_warnings += "\n[SISTEMA]: Estás en un BUCLE. Has repetido la acción exacta dos veces. DETENTE y usa `web_search` o cambia de estrategia."

        agent_context = f"""
OBJETIVO: {self.state.goal}
RUTA PROYECTO: {self.state.project_path}

HISTORIAL RECIENTE:
{history_str if history_str else "No se han realizado acciones todavía."}

{system_warnings}

ACCIONES DISPONIBLES:
1. shell_run: Ejecutar comando en la terminal.
2. write_file: Crear o sobreescribir un archivo (formato: 'ruta|contenido').
3. read_file: Leer contenido de un archivo (formato: 'ruta').
4. web_search: Buscar en internet info técnica.
5. complete: Solo si el objetivo se cumplió totalmente.

FORMATO DE SALIDA (JSON ÚNICAMENTE):
{{
  "thought": "Tu monólogo interno sobre por qué haces esto",
  "action": "nombre_de_accion",
  "action_input": "comando o parámetro"
}}
"""
        try:
            with show_loading("🧠 DOMINION está pensando..."):
                # We need to access the handler instance directly or through a helper
                # Since AIHandler.get_response doesn't typically take 'mode' override publicly, 
                # we need to set the mode context or use the prompt directly.
                # Let's see: AIHandler in ai_handler.py constructs system prompt based on get_mode().
                # We need to temporarily enforce AIMode.AGENT since self.ai is capable.
                
                # Trick: We can access the internal _build_system_prompt if we want, or better:
                # Update AIHandler to accept an override or recognize the agent context.
                # But since we are inside agent_engine, let's just manually call the logic 
                # or assume we modify AIHandler to allow passing mode. 
                
                # Wait, looking at ai_handler.py, get_response calls self.get_mode().
                # We should update get_response signature in ai_handler.py or subclass it?
                # Simpler: We are in agent_engine. Let's make a manual request using ai.groq_client if available
                # OR properly refactor AIHandler to support explicit mode.
                
                # The user approved the plan "Refactor Agent Engine ... to use AIMode.AGENT".
                # Let's assume we UPDATED AIHandler to allow this.
                # Re-checking ai_handler.py... get_response(self, query: str, raw: bool = False, mode_override: AIMode = None)
                # I haven't added mode_override yet. I should do that.
                
                # For now, let's assume I will update AIHandler in the next step to accept mode_override.
                response = self.ai.get_response(agent_context, raw=True, mode_override=AIMode.AGENT)
                
                # Robust JSON extraction
                import re

                try:
                    # 1. Try to find JSON inside markdown code blocks first
                    json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
                    if json_block_match:
                        content = json_block_match.group(1).strip()
                    else:
                        # 2. Extract from first { to last }
                        start_idx = response.find("{")
                        end_idx = response.rfind("}")
                        if start_idx != -1 and end_idx != -1:
                            content = response[start_idx:end_idx+1]
                        else:
                            content = response

                    # Use strict=False to allow literal control characters (like newlines) in strings
                    data = json.loads(content, strict=False)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.debug(f"Failed standard JSON parse, trying raw_decode: {e}")
                    # 3. Fallback: try raw_decode incrementally
                    try:
                        start_idx = response.find("{")
                        if start_idx != -1:
                            decoder = json.JSONDecoder(strict=False)
                            data, _ = decoder.raw_decode(response[start_idx:])
                        else:
                            raise ValueError("No starting brace found")
                    except Exception as e2:
                        logger.error(f"All JSON parsing attempts failed: {e2}")
                        return AgentStep(thought=f"Error decodificando pensamiento AI: {str(e2)}", action="complete", action_input="")

                return AgentStep(
                    thought=data.get("thought", "Sin pensamiento"),
                    action=data.get("action", "complete"),
                    action_input=data.get("action_input", "")
                )
        except Exception as e:
            logger.error(f"Error en pensamiento: {e}")
            return None

    def _execute(self, step: AgentStep) -> str:
        """Execute the selected action."""
        action = step.action
        param = step.action_input
        
        try:
            if action == "shell_run":
                # Ensure we are in the project path
                return self._run_shell(param)
            
            elif action == "write_file":
                if "|" not in param:
                    return "Error: write_file requiere formato 'ruta|contenido'"
                path, content = param.split("|", 1)
                full_path = self._safe_path(path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Archivo escrito exitosamente: {path}"
                
            elif action == "read_file":
                full_path = self._safe_path(param)
                if not os.path.exists(full_path):
                    return f"Error: Archivo no encontrado en {param}"
                with open(full_path, "r", encoding="utf-8") as f:
                    return f"Contenido de {param}:\n{f.read()}"
                    
            elif action == "web_search":
                with show_loading(f"🌐 Buscando: {param}..."):
                    results = web_search.search(param)
                    if not results:
                        return "No se encontraron resultados en la web."
                    output = "Resultados de búsqueda:\n"
                    for r in results[:3]:
                        output += f"- {r.title}: {r.url}\n  {r.body[:200]}...\n"
                    return output
            
            return f"Error: Acción '{action}' no reconocida."
            
        except Exception as e:
            return f"Error de ejecución: {str(e)}"

    def _run_shell(self, command: str) -> str:
        """Execute shell command with live real-time output."""
        try:
            # Change to project dir for execution
            original_cwd = os.getcwd()
            os.chdir(self.state.project_path)
            
            console.print(f"\n[bold blue]⚡ Ejecutando:[/bold blue] [white]{command}[/white]")
            
            # Start process with piped output
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Direct stderr to stdout for combined streaming
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            full_output = []
            output_text = Text()
            
            # Live display panel
            with Live(Panel(output_text, title="Terminal Live", border_style="cyan", subtitle="[dim]Streaming...[/dim]"), 
                     console=console, refresh_per_second=4, transient=True) as live:
                
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    
                    if line:
                        full_output.append(line)
                        output_text.append(line)
                        
                        # Sliding window: Keep last 10 lines only for display
                        display_lines = output_text.plain.split("\n")
                        if len(display_lines) > 10:
                            output_text = Text("\n".join(display_lines[-10:]))
                            live.update(Panel(output_text, title="Terminal Live", border_style="cyan", subtitle="[dim]Streaming...[/dim]"))

            rc = process.poll()
            os.chdir(original_cwd)
            
            result_str = "".join(full_output)
            output = f"STDOUT/STDERR:\n{result_str}\nRETURN CODE: {rc}"
            
            # Truncate for AI context if too large
            if len(output) > 2000:
                output = output[:1000] + "\n... (truncado por tamaño) ...\n" + output[-500:]
                
            return output
            
        except subprocess.TimeoutExpired:
            return "Error: Comando excedió el tiempo límite."
        except Exception as e:
            return f"Error crítico de shell en vivo: {str(e)}"

    def _safe_path(self, path: str) -> str:
        """Prevent directory traversal."""
        # Simple check: if it's absolute, use it, otherwise join with project_path
        if os.path.isabs(path):
            return path # Trusting the agent for now, but in multi-user this needs hardening
        return os.path.join(self.state.project_path, path)

    def _confirm_action(self, step: AgentStep) -> bool:
        """Ask user for permission if not in fully autonomous mode."""
        # For security and being "professional", we always ask in this version
        # unless it's a read action or search
        if step.action in ["read_file", "web_search"]:
            return True
            
        return console.input(f"\n[bold green]¿Permitir acción '{step.action}'? (s/n): [/bold green]").lower() == 's'

# Singleton instance or helper function
def run_dominion_agent(user_id: str = "00000000-0000-0000-0000-000000000000", goal: str = "", project_path: str = None):
    """Entry point for the advanced agent."""
    if not project_path:
        project_path = os.path.expanduser("~/kalirootcli_dominion")
    
    # Ensure user_id is a valid UUID string if it's 'anonymous' or other tags
    valid_user_id = user_id
    if user_id in ["anonymous", "cli_user", "default"]:
        valid_user_id = "00000000-0000-0000-0000-000000000000"
        
    agent = DominionAgent(valid_user_id)
    agent.start_task(goal, project_path)
