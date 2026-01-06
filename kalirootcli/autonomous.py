"""
Autonomous Security Agent Module - DOMINION
Professional semi-autonomous pentesting assistant with AI-powered command suggestions.
"""

import sys
import subprocess
import shutil
import logging
from typing import List, Dict, Any, Optional
from .api_client import api_client
from .ui.display import console, print_info, print_success, print_error, show_loading, Panel
from .distro_detector import detector

logger = logging.getLogger(__name__)


class AutonomousAgent:
    """Advanced Semi-Autonomous Security Agent with DOMINION logic."""
    
    def __init__(self, target: str):
        self.target = target
        self.history: List[str] = []
        self.distro = detector.distro
        self.distro_name = detector.get_distro_name()
        self.step = 0
        
    def _get_install_command(self, tool: str) -> str:
        """Get the appropriate install command based on distro."""
        distro_lower = self.distro.lower()
        
        if "termux" in distro_lower:
            return f"pkg install {tool}"
        elif "kali" in distro_lower or "debian" in distro_lower or "ubuntu" in distro_lower:
            return f"sudo apt install -y {tool}"
        elif "arch" in distro_lower:
            return f"sudo pacman -S --noconfirm {tool}"
        elif "fedora" in distro_lower or "rhel" in distro_lower:
            return f"sudo dnf install -y {tool}"
        else:
            return f"sudo apt install -y {tool}"  # Default
    
    def _check_tool_installed(self, tool: str) -> bool:
        """Check if a tool is installed."""
        return shutil.which(tool) is not None
    
    def _extract_tool_name(self, command: str) -> Optional[str]:
        """Extract the main tool name from a command."""
        if not command:
            return None
        parts = command.split()
        if parts:
            # Skip sudo if present
            tool = parts[0]
            if tool == "sudo" and len(parts) > 1:
                tool = parts[1]
            return tool
        return None
    
    def _ai_query(self, prompt: str) -> Dict[str, Any]:
        """Make AI query with proper credit deduction."""
        result = api_client.ai_query(prompt, environment={
            "distro": self.distro_name, 
            "target": self.target,
            "history": "\n".join(self.history[-5:])
        })
        return result
    
    def _get_next_command(self) -> str:
        """Get next command suggestion from AI."""
        context = "\n".join(self.history[-3:]) if self.history else "Inicio de operación."
        
        prompt = f"""
        SISTEMA: {self.distro_name}
        OBJETIVO: {self.target}
        HISTORIAL: {context}
        
        Eres un experto en ciberseguridad realizando una auditoría autorizada.
        Sugiere el siguiente comando EXACTO a ejecutar.
        Si la auditoría está completa, responde exactamente: DONE
        
        IMPORTANTE: Retorna SOLO el comando, sin explicaciones.
        """
        
        with show_loading("🤖 Analizando siguiente paso..."):
            result = self._ai_query(prompt)
            
        if result["success"]:
            response = result["data"].get("response", "DONE")
            return self._clean_command(response)
        else:
            error_msg = result.get("error", "Error desconocido")
            print_error(f"Error AI: {error_msg}")
            return ""
    
    def _request_specific_tool(self) -> str:
        """Let user request a specific tool or action."""
        console.print("\n[bold cyan]🔧 ¿Qué herramienta o acción deseas usar?[/bold cyan]")
        console.print("[dim]Ejemplos: 'usa nikto', 'escanea con nmap', 'busca directorios'[/dim]\n")
        
        user_request = console.input("[bold green]Tu petición: [/bold green]").strip()
        
        if not user_request:
            return ""
        
        prompt = f"""
        SISTEMA: {self.distro_name}
        OBJETIVO: {self.target}
        PETICIÓN DEL USUARIO: {user_request}
        
        El usuario quiere usar una herramienta específica o realizar una acción.
        Genera el comando EXACTO que mejor cumpla su petición.
        
        IMPORTANTE: Retorna SOLO el comando ejecutable, sin explicaciones.
        """
        
        with show_loading("🤖 Generando comando..."):
            result = self._ai_query(prompt)
            
        if result["success"]:
            response = result["data"].get("response", "")
            return self._clean_command(response)
        else:
            print_error(result.get("error", "Error"))
            return ""
    
    def _explain_situation(self) -> None:
        """Generate AI explanation of current situation."""
        context = "\n".join(self.history[-5:]) if self.history else "Sin actividad previa."
        
        prompt = f"""
        SISTEMA: {self.distro_name}
        OBJETIVO: {self.target}
        HISTORIAL DE COMANDOS:
        {context}
        
        Analiza la situación actual y responde en este formato EXACTO:

        ## PROGRESO
        [Describe brevemente qué comandos se han ejecutado y qué se intentó hacer]

        ## HALLAZGOS
        [Lista los descubrimientos importantes: puertos, servicios, vulnerabilidades, etc.]

        ## PRÓXIMOS PASOS
        [Sugiere 2-3 acciones concretas con comandos específicos]

        Sé técnico y directo. Usa formato markdown.
        """
        
        with show_loading("🧠 Analizando situación..."):
            result = self._ai_query(prompt)
            
        if result["success"]:
            explanation = result["data"].get("response", "")
            
            # Format the response with Rich markup
            formatted = self._format_analysis(explanation)
            
            console.print()
            console.print("[bold rgb(0,255,255)]╔══════════════════════════════════════════════════════════════╗[/bold rgb(0,255,255)]")
            console.print("[bold rgb(0,255,255)]║[/bold rgb(0,255,255)]           [bold]🧠 ANÁLISIS DE SITUACIÓN[/bold]                          [bold rgb(0,255,255)]║[/bold rgb(0,255,255)]")
            console.print("[bold rgb(0,255,255)]╚══════════════════════════════════════════════════════════════╝[/bold rgb(0,255,255)]")
            console.print()
            console.print(formatted)
            console.print()
        else:
            print_error(result.get("error", "Error al analizar"))
        
        console.print("\n[dim]Presiona Enter para continuar...[/dim]")
        input()
    
    def _format_analysis(self, text: str) -> str:
        """Format analysis text with Rich markup."""
        import re
        
        # Remove markdown code blocks (```bash ... ```)
        text = re.sub(r'```\w*\n?', '', text)
        
        # Bold markdown headers
        text = re.sub(r'^## (.+)$', r'\n[bold cyan]━━━ \1 ━━━[/bold cyan]', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'[bold yellow]▸ \1[/bold yellow]', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.+)$', r'[bold white]  • \1[/bold white]', text, flags=re.MULTILINE)
        
        # Bold numbered lists
        text = re.sub(r'^(\d+)\.\s+\*\*(.+?)\*\*', r'[bold yellow]\1.[/bold yellow] [bold]\2[/bold]', text, flags=re.MULTILINE)
        
        # Highlight commands in backticks (single)
        text = re.sub(r'`([^`\n]+)`', r'[bold green]\1[/bold green]', text)
        
        # Highlight IPs
        text = re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', r'[cyan]\1[/cyan]', text)
        
        # Highlight ports
        text = re.sub(r'(\d+/tcp|\d+/udp)', r'[yellow]\1[/yellow]', text)
        
        # Highlight important words
        text = text.replace("abierto", "[green]abierto[/green]")
        text = text.replace("cerrado", "[red]cerrado[/red]")
        text = text.replace("filtrado", "[yellow]filtrado[/yellow]")
        text = text.replace("vulnerab", "[bold red]vulnerab[/bold red]")
        
        # Clean up excess newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _handle_missing_tool(self, tool: str) -> bool:
        """Handle case when a tool is not installed."""
        console.print(f"\n[yellow]⚠️ Herramienta no encontrada: {tool}[/yellow]")
        
        install_cmd = self._get_install_command(tool)
        console.print(f"[dim]Comando de instalación sugerido: {install_cmd}[/dim]\n")
        
        action = console.input(f"[bold green]¿Instalar {tool}? (s/n): [/bold green]").lower()
        
        if action == 's':
            try:
                with show_loading(f"📦 Instalando {tool}..."):
                    process = subprocess.run(
                        install_cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                
                if process.returncode == 0:
                    print_success(f"✅ {tool} instalado correctamente")
                    return True
                else:
                    print_error(f"Error instalando {tool}: {process.stderr[:200]}")
                    return False
                    
            except Exception as e:
                print_error(f"Error: {e}")
                return False
        
        return False
    
    def _execute_command(self, command: str) -> bool:
        """Execute a command and capture output."""
        tool = self._extract_tool_name(command)
        
        # Check if tool is installed
        if tool and not self._check_tool_installed(tool):
            if not self._handle_missing_tool(tool):
                return False
        
        try:
            with show_loading(f"⚡ Ejecutando: {command[:50]}..."):
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            
            output = process.stdout + process.stderr
            
            if process.returncode == 0:
                print_success("Comando ejecutado correctamente")
            else:
                print_error(f"Comando finalizó con código: {process.returncode}")
            
            # Save to history
            obs_text = output[:2000] if len(output) > 2000 else output
            self.history.append(f"CMD: {command}\nOUT: {obs_text}")
            
            # Display output
            if output.strip():
                display_output = output.strip()[:1500]
                console.print(Panel(
                    display_output,
                    title="[bold]📺 Salida[/bold]",
                    border_style="dim"
                ))
            
            return True
            
        except subprocess.TimeoutExpired:
            print_error("Timeout: El comando tardó demasiado")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            self.history.append(f"CMD: {command}\nERR: {str(e)}")
            return False
    
    def _clean_command(self, text: str) -> str:
        """Extract command from AI response."""
        import re
        # Remove rich tags
        text = re.sub(r'\[.*?\]', '', text)
        # Remove markdown
        text = text.replace("```bash", "").replace("```", "").strip()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(("#", "Acceso", "Error")):
                return line
        return ""
    
    def _show_menu(self) -> None:
        """Show available options."""
        console.print()
        console.print("[dim]━━━━━━━━━━━━━━ OPCIONES ━━━━━━━━━━━━━━[/dim]")
        console.print("  [bold green]s[/bold green]  🚀 Ejecutar sugerencia")
        console.print("  [bold yellow]n[/bold yellow]  🔄 Saltar / Nueva sugerencia")
        console.print("  [bold cyan]e[/bold cyan]  ✏️  Editar comando")
        console.print("  [bold magenta]r[/bold magenta]  🔧 Solicitar herramienta")
        console.print("  [bold blue]a[/bold blue]  🧠 Analizar situación")
        console.print("  [bold red]q[/bold red]  🚪 Salir")
        console.print("[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
    
    def run_loop(self):
        """Execute the main autonomous loop."""
        console.print(Panel(
            f"[bold]🎯 Objetivo:[/bold] {self.target}\n"
            f"[bold]💻 Sistema:[/bold] {self.distro_name}\n\n"
            "[dim]El agente sugerirá comandos basados en el objetivo.\n"
            "Tú decides qué ejecutar. Cada consulta AI = 1 crédito.[/dim]",
            title="[bold rgb(0,255,255)]🚀 DOMINION AGENT[/bold rgb(0,255,255)]",
            border_style="rgb(0,255,255)"
        ))
        
        # Main loop - no step limit
        while True:
            self.step += 1
            console.rule(f"[bold cyan]─── Paso {self.step} ───[/bold cyan]")
            
            # Get AI suggestion
            next_command = self._get_next_command()
            
            if not next_command or "DONE" in next_command.upper():
                print_success("✅ Auditoría completada")
                break
            
            # Show suggestion
            console.print(f"\n[bold yellow]👉 Sugerencia:[/bold yellow] [white]{next_command}[/white]")
            
            # Show menu
            self._show_menu()
            
            # Get user action
            action = console.input("\n[bold green]Acción: [/bold green]").lower().strip()
            
            if action == 'q':
                console.print("[dim]Saliendo del agente...[/dim]")
                break
                
            elif action == 's' or action == '':
                self._execute_command(next_command)
                
            elif action == 'n':
                print_info("Obteniendo nueva sugerencia...")
                continue
                
            elif action == 'e':
                edited = console.input("[bold cyan]Nuevo comando: [/bold cyan]").strip()
                if edited:
                    self._execute_command(edited)
                    
            elif action == 'r':
                custom_cmd = self._request_specific_tool()
                if custom_cmd:
                    console.print(f"\n[bold yellow]👉 Comando generado:[/bold yellow] {custom_cmd}")
                    confirm = console.input("[bold green]¿Ejecutar? (s/n): [/bold green]").lower()
                    if confirm == 's':
                        self._execute_command(custom_cmd)
                        
            elif action == 'a':
                self._explain_situation()
            
            else:
                print_info("Opción no reconocida. Usa s/n/e/r/a/q")


def run_autonomous_mode(target: str, user_id: str = None):
    """Entry point for autonomous mode."""
    if not api_client.is_logged_in():
        print_error("❌ Debes iniciar sesión para usar el modo autónomo")
        print_info("Ejecuta: kr-clidn y haz login")
        return
    
    try:
        agent = AutonomousAgent(target)
        agent.run_loop()
    except KeyboardInterrupt:
        console.print("\n")
        console.print("[bold cyan]👋 Sesión de DOMINION Agent interrumpida[/bold cyan]")
        console.print("[dim]Gracias por usar KR-CLI. ¡Hasta pronto![/dim]\n")
