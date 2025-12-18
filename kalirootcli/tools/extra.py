"""
Extra utilities for the tools menu.
"""
import os
import sys
import subprocess
import webbrowser
from rich.console import Console

console = Console()


def _clear_terminal() -> None:
    """Clear the terminal COMPLETELY - no trace left."""
    # ANSI escape sequences for complete clear
    sys.stdout.write('\033[H\033[2J\033[3J')
    sys.stdout.flush()
    
    # System clear command
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear -x 2>/dev/null || clear')
    
    # Rich console clear
    console.clear()

def install_gdown():
    """Install gdown if not present."""
    try:
        import gdown
        return True
    except ImportError:
        console.print("[yellow]Instalando gdown...[/yellow]")
        try:
            subprocess.run(["pip", "install", "gdown"], check=True)
            return True
        except Exception as e:
            console.print(f"[red]Error instalando gdown: {e}[/red]")
            return False

def gdrive_downloader():
    """Download file from Google Drive using ID."""
    console.print("\n[bold cyan]📥 GOOGLE DRIVE DOWNLOADER[/bold cyan]")
    console.print("[dim]Descarga directa usando File ID[/dim]\n")
    
    if not install_gdown():
        return

    file_id = input("📂 Ingresa el Google Drive File ID: ").strip()
    if not file_id:
        return
        
    output_name = input("💾 Nombre de archivo de salida (opcional): ").strip()
    
    cmd = ["gdown", file_id]
    if output_name:
        cmd.extend(["-O", output_name])
        
    console.print(f"\n[dim]Ejecutando: {' '.join(cmd)}[/dim]")
    try:
        subprocess.run(cmd, check=True)
        console.print("\n[bold green]✅ Descarga completada[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error en la descarga: {e}[/bold red]")
    
    input("\nPresiona Enter para continuar...")

def show_metasploit_resources():
    """Show Metasploit resources and links."""
    while True:
        _clear_terminal()
        console.print("\n[bold red]⚡ METASPLOIT RESOURCES[/bold red]\n")
        
        options = [
            ("1", "Metasploit Unleashed (Free Course)", "https://www.offsec.com/metasploit-unleashed/"),
            ("2", "Rapid7 Documentation", "https://docs.rapid7.com/metasploit/"),
            ("3", "Metasploit GitHub", "https://github.com/rapid7/metasploit-framework"),
            ("4", "Exploit Database", "https://www.exploit-db.com/"),
            ("5", "CX Security", "https://cxsecurity.com/")
        ]
        
        for key, name, url in options:
            console.print(f" {key} › [bold]{name}[/bold]")
            console.print(f"     [blue underline]{url}[/blue underline]\n")
            
        console.print(" 0 › Volver")
        
        choice = input("\nSelecciona para abrir (0-5): ").strip()
        
        if choice == "0":
            break
            
        for key, name, url in options:
            if choice == key:
                webbrowser.open(url)
                console.print(f"[green]Abriendo {name}...[/green]")
                input("Presiona Enter...")
