"""
Smart Command Wrapper for KaliRoot CLI (kr-cli)
Executes commands and analyzes output for vulnerabilities/next steps.
Includes Reporting capabilities.
"""

import sys
import subprocess
import shutil
import logging
from .ui.display import console, print_info, print_success, print_error, show_loading, print_ai_response
from .database_manager import get_chat_history, get_user_profile
from rich.prompt import Prompt
import warnings
# Suppress ResourceWarning for cleaner CLI output
warnings.simplefilter("ignore", ResourceWarning)

from .reporting import ReportGenerator

# Setup logging
logger = logging.getLogger(__name__)

from .api_client import api_client

TABLE_HEADER = "[bold rgb(0,255,255)]KaliRoot CLI[/bold rgb(0,255,255)]"

def execute_and_analyze(args):
    """Execute command and analyze key outputs."""
    if not args:
        return

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
            
        # 2. Universal Analysis Prompt
        # Verify we have actual output to analyze
        valid_output = (stdout and len(stdout.strip()) > 5) or (stderr and len(stderr.strip()) > 5)
        
        if valid_output:
            # Check if user is logged in
            if not api_client.is_logged_in():
                # Passive suggestion if not logged in
                return
            
            # Confirm analysis
            console.print(f"\n[bold rgb(0,255,255)]✨ Análisis de IA disponible (1 crédito)[/bold rgb(0,255,255)]")
            confirm_analysis = Prompt.ask("¿Analizar resultados?", choices=["Y", "n"], default="Y")
            
            if confirm_analysis.lower() == "n":
                return
                
            user_id = api_client.user_id 
            
            output_to_analyze = stdout + "\n" + stderr
            output_to_analyze = output_to_analyze[-2000:] # Increased limit for better context
            
            # Build query for API
            query = (
                f"Actúa como un experto en ciberseguridad ofensiva y defensiva. "
                f"Analiza el resultado de la ejecución del comando: '{full_cmd}'.\n\n"
                f"Salida del comando:\n{output_to_analyze}\n\n"
                f"Tu tarea es:\n"
                f"1. Explicar brevemente qué se analizó (interpretación de la salida).\n"
                f"2. Identificar hallazgos clave (puertos, vulnerabilidades, errores, o éxito de la operación).\n"
                f"3. Sugerir los siguientes pasos técnicos o comandos a ejecutar.\n"
                f"Formato profesional, técnico y directo."
            )
            
            with show_loading("🧠 Analizando output con IA..."):
                # Use API client instead of direct AIHandler
                result = api_client.ai_query(query, environment={})
                
            if result["success"]:
                data = result["data"]
                # Use professional visualization
                response_text = data.get("response", "")
                if not isinstance(response_text, str):
                    response_text = str(response_text)

                print_ai_response(
                    response_text, 
                    mode=data.get("mode", "CONSULTATION"),
                    command=full_cmd
                )
                
                if data.get("credits_remaining") is not None:
                    console.print(f"[dim]💳 Créditos restantes: {data['credits_remaining']}[/dim]")
            else:
                error_msg = result.get("error", "Error desconocido")
                console.print(f"\n[bold red]❌ {error_msg}[/bold red]")
            
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
