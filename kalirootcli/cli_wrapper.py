"""
Smart Command Wrapper for KaliRoot CLI — DOMINION Edition
Executes commands and analyzes output for vulnerabilities/next steps.
KR economy: spend tracking for AI analysis and report generation.
"""

import sys
import subprocess
import shutil
import logging

from .ui.display import (
    console,
    print_info,
    print_success,
    print_error,
    show_loading,
    print_ai_response,
)
from .database_manager import get_chat_history, get_user_profile
from rich.prompt import Prompt
from rich.panel import Panel
import warnings

warnings.simplefilter("ignore", ResourceWarning)

from .reporting import ReportGenerator
from .api_client import api_client
from .economy import show_zero_balance_panel, show_kr_spend_panel
from .config import KR_COST_CHAT, KR_COST_REPORT, DOMINION_STORE_URL

logger = logging.getLogger(__name__)

TABLE_HEADER = "[bold rgb(0,255,255)]KaliRoot CLI — DOMINION[/bold rgb(0,255,255)]"


def execute_and_analyze(args):
    """Execute command and analyze output with DOMINION AI."""
    if not args:
        return

    command = args[0]
    full_cmd = " ".join(args)

    console.print(f"[dim]⚡ Ejecutando: {full_cmd}[/dim]")

    try:
        process = subprocess.run(args, capture_output=True, text=True)

        stdout = process.stdout
        stderr = process.stderr

        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        valid_output = (stdout and len(stdout.strip()) > 5) or (stderr and len(stderr.strip()) > 5)

        if valid_output:
            if not api_client.is_logged_in():
                return

            # KR balance check before offering AI analysis
            balance = api_client.get_kr_balance()
            if balance < KR_COST_CHAT:
                show_zero_balance_panel()
                return

            console.print(
                f"\n[bold rgb(0,255,255)]✨ Análisis DOMINION disponible "
                f"(-{KR_COST_CHAT} KR | Saldo: {balance} KR)[/bold rgb(0,255,255)]"
            )
            confirm_analysis = Prompt.ask(
                f"¿Analizar resultados? (-{KR_COST_CHAT} KR)",
                choices=["Y", "n"],
                default="Y",
            )

            if confirm_analysis.lower() == "n":
                return

            # Show spend panel
            show_kr_spend_panel(KR_COST_CHAT, "Análisis de Comando")

            user_id = api_client.user_id
            output_to_analyze = (stdout + "\n" + stderr)[-2000:]

            query = (
                f"Actúa como un experto en ciberseguridad ofensiva y defensiva. "
                f"Analiza el resultado de la ejecución del comando: '{full_cmd}'.\n\n"
                f"Salida del comando:\n{output_to_analyze}\n\n"
                f"Tu tarea es:\n"
                f"1. Explicar brevemente qué se analizó (interpretación de la salida).\n"
                f"2. Identificar hallazgos clave (puertos, vulnerabilidades, errores, o éxito).\n"
                f"3. Sugerir los siguientes pasos técnicos o comandos a ejecutar.\n"
                f"Formato profesional, técnico y directo."
            )

            with show_loading("🧠 Analizando output con DOMINION AI..."):
                result = api_client.ai_query(query, environment={})

            if result["success"]:
                data = result["data"]
                response_text = data.get("response", "")
                if not isinstance(response_text, str):
                    response_text = str(response_text)

                print_ai_response(
                    response_text,
                    mode=data.get("mode", "OPERATIONAL"),
                    command=full_cmd,
                )

                new_balance = api_client.get_kr_balance()
                console.print(f"[dim]⚡ KR restantes: {new_balance}[/dim]")
            else:
                error_msg = result.get("error", "Error desconocido")
                if "insuficiente" in error_msg.lower() or "insufficient" in error_msg.lower():
                    show_zero_balance_panel()
                else:
                    console.print(f"\n[bold red]❌ {error_msg}[/bold red]")

    except FileNotFoundError:
        print_error(f"Comando no encontrado: {command}")
    except KeyboardInterrupt:
        print_error("\nEjecución interrumpida.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Error de ejecución: {e}")


def handle_report():
    """Generate executive report — costs KR_COST_REPORT KR."""
    if not api_client.is_logged_in() or not api_client.user_id:
        print_error("❌ Debes iniciar sesión: kr-cli login")
        return

    user_id = api_client.user_id

    # KR balance check
    balance = api_client.get_kr_balance()
    if balance < KR_COST_REPORT:
        show_zero_balance_panel()
        console.print(
            Panel(
                f"[red]La generación de reportes requiere [bold]{KR_COST_REPORT} KR[/bold].\n"
                f"Tu saldo actual: [bold]{balance} KR[/bold].[/red]\n\n"
                f"[cyan]Recarga en:[/cyan] [link={DOMINION_STORE_URL}]{DOMINION_STORE_URL}[/link]",
                title="[bold yellow]⚡ KR INSUFICIENTES[/bold yellow]",
                border_style="red",
            )
        )
        return

    # Show spend panel
    show_kr_spend_panel(KR_COST_REPORT, "Generación de Reporte Ejecutivo")

    with show_loading("📄 Generando Reporte Ejecutivo DOMINION..."):
        history = get_chat_history(user_id, limit=20)
        if not history:
            print_error("No hay historial suficiente para generar un reporte.")
            return

        from .ai_handler import AIHandler
        ai = AIHandler(user_id)
        session_data = ai.analyze_session_for_report(history)

        session_data["raw_log"] = history

        gen = ReportGenerator()
        pdf_path = gen.generate_report(session_data)

    print_success(f"✅ Reporte generado: {pdf_path}")

    new_balance = api_client.get_kr_balance()
    console.print(f"[dim]⚡ KR restantes: {new_balance}[/dim]")


from .autonomous import run_autonomous_mode
from .audio import listen_and_execute


def main():
    """Entry point for kr-cli."""
    if len(sys.argv) < 2:
        print_info("Uso: kr-cli <comando> [args...]")
        print_info("     kr-cli report")
        print_info("     kr-cli auto <objetivo>")
        print_info("     kr-cli listen")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "report":
        handle_report()
    elif cmd == "auto":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        if not target:
            print_error("Objetivo requerido: kr-cli auto <objetivo>")
            return
        run_autonomous_mode(target)
    elif cmd == "listen":
        transcript = listen_and_execute()
        if transcript:
            print_info(f"⚡ Ejecutando comando de voz: {transcript}")
            execute_and_analyze(transcript.split())
    else:
        execute_and_analyze(sys.argv[1:])


if __name__ == "__main__":
    main()
