"""
Smart Command Wrapper for KaliRoot CLI (kr-cli)
Executes commands and analyzes output for vulnerabilities/next steps.
"""

# ... (omitted)

def main():
    """Entry point for kr-cli."""
    if len(sys.argv) < 2:
        print_info("Usage: kr-cli <command> [args...]")
        print_info("Example: kr-cli nmap -sV localhost")
        sys.exit(1)
        
    execute_and_analyze(sys.argv[1:])

if __name__ == "__main__":
    main()
