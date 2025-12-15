"""
Smart Command Wrapper for KaliRoot CLI (kr-cli)
Executes commands and analyzes output for vulnerabilities/next steps.
Includes Reporting capabilities.
"""

import sys
import subprocess
import shutil
import logging
from .ui.display import console, print_info, print_success, print_error, show_loading
from .database_manager import get_chat_history, get_user_profile
from rich.prompt import Prompt
import warnings
# Suppress ResourceWarning for cleaner CLI output
warnings.simplefilter("ignore", ResourceWarning)

from .reporting import ReportGenerator

# Setup logging
logger = logging.getLogger(__name__)

from .api_client import api_client

TABLE_HEADER = "[bold cyan]KaliRoot CLI[/bold cyan]"

# Tools that trigger AI analysis
ANALYSIS_TARGETS = ['nmap', 'gobuster', 'sqlmap', 'nikto', 'wfuzz', 'hydra', 'metasploit', 'msfconsole']

def execute_and_analyze(args):
    """Execute command and analyze key outputs."""
    command = args[0]
    full_cmd = " ".join(args)
    
    # 1. Execute Command
    console.print(f"[dim]⚡ Executing: {full_cmd}[/dim]")
    
    try:
        # Run command and stream output
        # using subprocess.run for simplicity in capturing everything
        process = subprocess.run(
            args, 
            capture_output=True, 
            text=True
        )
        
        stdout = process.stdout
        stderr = process.stderr
        
        # Print output to user
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
            
        # 2. Analyze if relevant
        if command in ANALYSIS_TARGETS or any(t in command for t in ANALYSIS_TARGETS):
            # Check if user is logged in
            if not api_client.is_logged_in():
                console.print("\n[yellow]⚠️  No estás autenticado[/yellow]")
                print_info("ℹ️ Inicia sesión para análisis AI: kr-cli login")
                return
            
            # Confirm analysis
            console.print(f"\n[bold cyan]✨ Análisis de IA disponible (Costo: 1 crédito)[/bold cyan]")
            confirm_analysis = Prompt.ask("¿Analizar salida con IA?", choices=["Y", "n"], default="Y")
            
            if confirm_analysis.lower() == "n":
                return
                
            user_id = api_client.user_id 
            
            output_to_analyze = stdout + "\n" + stderr
            output_to_analyze = output_to_analyze[-1500:] # Strict limit for tokens
            
            # Build query for API
            query = f"Analiza la siguiente salida del comando '{full_cmd}':\n\n{output_to_analyze}\n\nIdentifica vulnerabilidades, puertos abiertos, servicios y sugiere próximos pasos."
            
            with show_loading("🧠 Analyzing results..."):
                # Use API client instead of direct AIHandler
                result = api_client.ai_query(query, environment={})
                
            if result["success"]:
                data = result["data"]
                console.print("\n[bold cyan]🧠 AI ANALYSIS[/bold cyan]")
                console.print(data["response"])
                
                if data.get("credits_remaining") is not None:
                    console.print(f"\n[dim]💳 Créditos restantes: {data['credits_remaining']}[/dim]")
            else:
                error_msg = result.get("error", "Error desconocido")
                console.print(f"\n[red]❌ {error_msg}[/red]")
            
    except FileNotFoundError:
        print_error(f"Command not found: {command}")
    except KeyboardInterrupt:
        print_error("\nExecution interrupted.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Execution error: {e}")

def handle_report():
    """Generate PDF report from recent session."""
    if not api_client.is_logged_in() or not api_client.user_id:
        print_error("❌ Debes iniciar sesión para generar reportes: kr-cli login")
        return
        
    user_id = api_client.user_id
    
    with show_loading("Generando reporte ejecutivo..."):
        # 1. Fetch History
        history = get_chat_history(user_id, limit=20)
        if not history:
            print_error("No hay historial suficiente para generar un reporte.")
            return

        # 2. AI Summarization
        ai = AIHandler(user_id)
        session_data = ai.analyze_session_for_report(history)
        
        # Add raw log for appendix
        session_data['raw_log'] = history
        
        # 3. Generate PDF
        gen = ReportGenerator()
        pdf_path = gen.generate_report(session_data)
        
    print_success(f"Reporte generado exitosamente: {pdf_path}")
    # Try to open it
    # shutil.which('xdg-open') and subprocess.run(['xdg-open', pdf_path])

from .autonomous import run_autonomous_mode
from .audio import listen_and_execute

# ... (existing imports)

def main():
    """Entry point for kr-cli."""
    if len(sys.argv) < 2:
        print_info("Usage: kr-cli <command> [args...]")
        print_info("         kr-cli report")
        print_info("         kr-cli auto <target>")
        print_info("         kr-cli listen")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "report":
        handle_report()
    elif cmd == "auto":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        if not target:
            print_error("Target required: kr-cli auto <target>")
            return
        run_autonomous_mode(target)
    elif cmd == "listen":
        transcript = listen_and_execute()
        if transcript:
            print_info(f"⚡ Ejecutando comando de voz: {transcript}")
            # Simple assumption: transcript is a valid command string
            execute_and_analyze(transcript.split())
    else:
        execute_and_analyze(sys.argv[1:])

if __name__ == "__main__":
    main()
