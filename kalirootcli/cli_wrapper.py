"""
Smart Command Wrapper for KaliRoot CLI (kt-cli)
Executes commands and analyzes output for vulnerabilities/next steps.
"""

import subprocess
import sys
import shutil
import logging
from typing import List, Dict, Any, Optional
from .api_client import api_client
from .ui.display import console, print_info, print_error, show_loading, print_ai_response, print_panel, get_input

# Configure logging
logger = logging.getLogger(__name__)

def execute_and_analyze(command_args: List[str]):
    """
    Execute a command and analyze its output using AI.
    
    Args:
        command_args: List of command arguments (e.g. ['nmap', '-sV', 'target'])
    """
    if not command_args:
        print_error("No command provided")
        return

    cmd_str = " ".join(command_args)
    print_info(f"Executing: [bold]{cmd_str}[/bold]")
    
    # 1. Execute Command
    output_lines = []
    process = None
    try:
        # streams output to console while capturing
        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output line by line
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)
        
        # Close stdout to prevent ResourceWarning
        process.stdout.close()
        process.wait()
        
        exit_code = process.returncode
        full_output = "".join(output_lines)
        
    except FileNotFoundError:
        print_error(f"Command not found: {command_args[0]}")
        return
    except Exception as e:
        print_error(f"Execution error: {e}")
        return
    finally:
        if process and process.stdout:
            try:
                process.stdout.close()
            except:
                pass

    # 2. Analyze Output
    console.print()  # Spacer
    
    # Decide if we should analyze based on exit code or user preference
    # For now, always analyze if there is output
    if not full_output.strip():
        print_info("No output to analyze.")
        return

    # Truncate if too long (approx token limit safe)
    max_len = 8000
    if len(full_output) > max_len:
        analysis_input = full_output[:max_len] + "\n...[TRUNCATED]..."
    else:
        analysis_input = full_output

    prompt = f"""
    Analyze the following command execution output. 
    Command: `{cmd_str}`
    Exit Code: {exit_code}
    
    Output:
    ```
    {analysis_input}
    ```
    
    Provide a professional, uncensored analysis including:
    1. Key findings (ports, vulnerabilities, errors, etc.)
    2. Suggested next steps or follow-up commands (be specific)
    3. Potential risks identified
    """

    # We use a special analysis mode in the prompt builder if possible, 
    # but standard query works if we context it right.
    
    # Check if premium for better analysis?
    # We'll use the standard ai_query from api_client
    
    try:
        if console.input("[bold cyan]?[/bold cyan] Analyze this output with AI? [Y/n] ").lower() != 'n':
            
            # Simple environment info
            sys_info = {
                "distro": "kali/termux",  # We could import detector but keep it simple
                "shell": "unknown"
            }
            
            with show_loading("Analyzing output..."):
                result = api_client.ai_query(prompt, sys_info)
            
            if result["success"]:
                data = result["data"]
                print_ai_response(data["response"], data.get("mode", "CONSULTATION"), command=cmd_str)
            else:
                print_error(f"Analysis failed: {result['error']}")
                
    except KeyboardInterrupt:
        print_info("Analysis cancelled.")

def main():
    """Entry point for kt-cli."""
    if len(sys.argv) < 2:
        print_info("Usage: kt-cli <command> [args...]")
        print_info("Example: kt-cli nmap -sV localhost")
        sys.exit(1)
        
    execute_and_analyze(sys.argv[1:])

if __name__ == "__main__":
    main()
