"""
Agent Module for KaliRootCLI
Professional file creation, project scaffolding, and planning capabilities.

Features:
- File creation from templates
- Project scaffolding (pentest, tool, audit, research)
- Project planning with documentation
- Code generation helpers
"""

import os
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Literal, Union
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProjectPlan:
    """Project planning structure."""
    name: str
    description: str
    objectives: List[str]
    phases: List[Dict] = field(default_factory=list)
    created_at: str = ""
    status: str = "planning"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.phases:
            self.phases = [
                {"name": "Fase 1: Planificación", "tasks": ["Definir alcance", "Establecer timeline"], "status": "pending"},
                {"name": "Fase 2: Ejecución", "tasks": ["Implementar", "Probar"], "status": "pending"},
                {"name": "Fase 3: Revisión", "tasks": ["Analizar resultados", "Documentar"], "status": "pending"}
            ]


@dataclass 
class FileCreationResult:
    """Result of file creation operation."""
    success: bool
    path: str = ""
    message: str = ""
    error: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES = {
    "python_script": '''#!/usr/bin/env python3
"""
{name}
{description}

Author: KaliRoot CLI Agent
Created: {date}
"""

import argparse
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="{description}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add your arguments here
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Output file")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("🚀 Starting {name}...")
        
        # Your code here
        
        logger.info("✅ Completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\\n⚠️ Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Error: {{e}}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
''',

    "python_class": '''#!/usr/bin/env python3
"""
{name}
{description}

Author: KaliRoot CLI Agent
Created: {date}
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class {class_name}Config:
    """Configuration for {class_name}."""
    debug: bool = False
    timeout: int = 30


class {class_name}:
    """
    {description}
    
    Usage:
        instance = {class_name}()
        result = instance.execute()
    """
    
    def __init__(self, config: Optional[{class_name}Config] = None):
        """Initialize {class_name}."""
        self.config = config or {class_name}Config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def execute(self) -> Dict[str, Any]:
        """
        Execute the main operation.
        
        Returns:
            Dict with results
        """
        self.logger.info("Executing {class_name}...")
        
        try:
            # Your implementation here
            result = {{
                "success": True,
                "data": None
            }}
            return result
            
        except Exception as e:
            self.logger.error(f"Error: {{e}}")
            return {{"success": False, "error": str(e)}}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    instance = {class_name}()
    result = instance.execute()
    print(result)
''',

    "bash_script": '''#!/bin/bash
#
# {name}
# {description}
#
# Author: KaliRoot CLI Agent
# Created: {date}
#

set -euo pipefail
IFS=$'\\n\\t'

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly LOG_FILE="/tmp/${{SCRIPT_NAME%.*}}.log"

# Colors
readonly RED='\\033[0;31m'
readonly GREEN='\\033[0;32m'
readonly YELLOW='\\033[1;33m'
readonly BLUE='\\033[0;34m'
readonly CYAN='\\033[0;36m'
readonly NC='\\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

log_info() {{
    echo -e "${{GREEN}}[INFO]${{NC}} $1" | tee -a "$LOG_FILE"
}}

log_warn() {{
    echo -e "${{YELLOW}}[WARN]${{NC}} $1" | tee -a "$LOG_FILE"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1" | tee -a "$LOG_FILE" >&2
}}

log_debug() {{
    if [[ "${{DEBUG:-false}}" == "true" ]]; then
        echo -e "${{CYAN}}[DEBUG]${{NC}} $1" | tee -a "$LOG_FILE"
    fi
}}

show_banner() {{
    echo -e "${{BLUE}}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    {name}                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${{NC}}"
}}

show_usage() {{
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

{description}

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -d, --debug     Enable debug mode
    
EXAMPLES:
    $SCRIPT_NAME
    $SCRIPT_NAME --verbose

EOF
}}

cleanup() {{
    log_debug "Cleaning up..."
    # Add cleanup tasks here
}}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

main() {{
    trap cleanup EXIT
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    show_banner
    log_info "Starting {name}..."
    
    # ═══════════════════════════════════════════════════════════════════════════
    # YOUR CODE HERE
    # ═══════════════════════════════════════════════════════════════════════════
    
    
    log_info "✅ Complete!"
}}

main "$@"
''',

    "security_audit": '''# 🛡️ Security Audit Report
## {name}

| Field | Value |
|-------|-------|
| **Created** | {date} |
| **Status** | 🟡 In Progress |
| **Auditor** | KaliRoot CLI |
| **Classification** | Confidential |

---

## 📋 Executive Summary

{description}

## 🎯 Scope

### In Scope
- [ ] Network infrastructure
- [ ] Web applications
- [ ] API endpoints
- [ ] Authentication systems

### Out of Scope
- Third-party services
- Physical security

---

## 🔍 Methodology

1. **Reconnaissance** - Information gathering
2. **Scanning** - Vulnerability scanning
3. **Exploitation** - Controlled testing
4. **Post-Exploitation** - Impact assessment
5. **Reporting** - Documentation

---

## 🚨 Findings Summary

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 0 | - |
| 🟠 High | 0 | - |
| 🟡 Medium | 0 | - |
| 🟢 Low | 0 | - |
| ℹ️ Info | 0 | - |

---

## 🔴 Critical Findings

*No critical findings identified.*

---

## 🟠 High Severity Findings

*No high severity findings identified.*

---

## 🟡 Medium Severity Findings

*No medium severity findings identified.*

---

## 🟢 Low Severity Findings

*No low severity findings identified.*

---

## 📊 Risk Matrix

```
Impact
  ▲
  │  Low    Medium   High
  │   🟢      🟡      🟠
  │   🟢      🟡      🔴
  │   🟡      🟠      🔴
  └──────────────────────▶ Likelihood
```

---

## ✅ Recommendations

1. **[Recommendation 1]**
   - Priority: High
   - Effort: Medium

2. **[Recommendation 2]**
   - Priority: Medium
   - Effort: Low

---

## 📅 Timeline

| Phase | Start | End | Status |
|-------|-------|-----|--------|
| Reconnaissance | - | - | ⏳ Pending |
| Scanning | - | - | ⏳ Pending |
| Exploitation | - | - | ⏳ Pending |
| Reporting | - | - | ⏳ Pending |

---

## 📎 Appendices

### A. Tools Used
- Nmap
- Burp Suite
- OWASP ZAP

### B. Evidence
*Attached separately*

---

*Generated by KaliRoot CLI | Confidential Document*
''',

    "project_plan": '''# 📋 Project Plan: {name}

| Field | Value |
|-------|-------|
| **Created** | {date} |
| **Author** | KaliRoot CLI |
| **Status** | 🟡 Planning |
| **Version** | 1.0 |

---

## 🎯 Overview

{description}

---

## 📌 Objectives

{objectives}

---

## 📊 Phases

{phases}

---

## ⏱️ Timeline

```mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Planning           :a1, 2024-01-01, 7d
    section Phase 2
    Execution          :a2, after a1, 14d
    section Phase 3
    Review             :a3, after a2, 7d
```

---

## 👥 Resources Required

- [ ] Team member 1
- [ ] Team member 2
- [ ] Tools/Software
- [ ] Infrastructure

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk 1 | Medium | High | Mitigation strategy |
| Risk 2 | Low | Medium | Mitigation strategy |

---

## ✅ Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## 📝 Notes

*Add project notes here*

---

*Generated by KaliRoot CLI*
''',

    "exploit_template": '''#!/usr/bin/env python3
"""
{name}
{description}

⚠️ DISCLAIMER: For authorized testing only.
Unauthorized access to computer systems is illegal.

Author: KaliRoot CLI Agent
Created: {date}
"""

import argparse
import logging
import socket
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Exploit:
    """
    {name} Exploit Class
    
    Target: [Specify target]
    CVE: [If applicable]
    """
    
    def __init__(self, target: str, port: int):
        self.target = target
        self.port = port
        self.socket: Optional[socket.socket] = None
        
    def connect(self) -> bool:
        """Establish connection to target."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.target, self.port))
            logger.info(f"Connected to {{self.target}}:{{self.port}}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {{e}}")
            return False
    
    def exploit(self) -> bool:
        """
        Execute the exploit.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.socket:
            if not self.connect():
                return False
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # EXPLOIT LOGIC HERE
            # ═══════════════════════════════════════════════════════════════
            
            payload = b""  # Your payload here
            
            logger.info("Sending payload...")
            self.socket.send(payload)
            
            response = self.socket.recv(1024)
            logger.info(f"Response: {{response}}")
            
            return True
            
        except Exception as e:
            logger.error(f"Exploit failed: {{e}}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.socket:
            self.socket.close()
            self.socket = None


def main():
    parser = argparse.ArgumentParser(
        description="{description}",
        epilog="⚠️ Use responsibly and only on authorized targets."
    )
    parser.add_argument("target", help="Target IP/hostname")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port")
    parser.add_argument("-v", "--verbose", action="store_true")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("""
    ⚠️  LEGAL DISCLAIMER  ⚠️
    
    This tool is for authorized penetration testing only.
    Unauthorized access is illegal and unethical.
    
    By proceeding, you confirm authorization to test the target.
    """)
    
    confirm = input("Do you have authorization? [y/N]: ")
    if confirm.lower() != 'y':
        print("Aborting.")
        return 1
    
    exploit = Exploit(args.target, args.port)
    
    if exploit.exploit():
        logger.info("✅ Exploit successful!")
        return 0
    else:
        logger.error("❌ Exploit failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_STRUCTURES = {
    "pentest": {
        "dirs": ["01_recon", "02_scan", "03_exploit", "04_post", "05_loot", "06_reports", "tools", "evidence"],
        "files": {
            "README.md": "# {name}\n\n🔓 Penetration Testing Project\n\n## Scope\n\n## Credentials\n\n## Timeline\n",
            "notes.md": "# Notas del Proyecto\n\n## Objetivos\n\n## Descubrimientos\n\n## Credenciales Encontradas\n",
            "checklist.md": "# Pentest Checklist\n\n## Reconocimiento\n- [ ] OSINT\n- [ ] DNS Enumeration\n- [ ] Subdomain discovery\n\n## Scanning\n- [ ] Port scan\n- [ ] Service detection\n- [ ] Vulnerability scan\n\n## Exploitation\n- [ ] Initial access\n- [ ] Privilege escalation\n\n## Post-Exploitation\n- [ ] Persistence\n- [ ] Lateral movement\n- [ ] Data exfiltration\n\n## Reporting\n- [ ] Executive summary\n- [ ] Technical details\n- [ ] Recommendations\n",
            "scope.txt": "# Scope Definition\n\nIn Scope:\n- \n\nOut of Scope:\n- \n\nRules of Engagement:\n- \n"
        }
    },
    "tool": {
        "dirs": ["src", "tests", "docs", "examples", "scripts"],
        "files": {
            "README.md": "# {name}\n\n## Description\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython -m src.main\n```\n\n## License\n\nMIT\n",
            "requirements.txt": "# Dependencies\nrequests>=2.31.0\nrich>=13.0.0\n",
            "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name=\"{name_lower}\",\n    version=\"0.1.0\",\n    packages=find_packages(),\n    install_requires=[\n        \"requests>=2.31.0\",\n    ],\n    entry_points={{\n        \"console_scripts\": [\n            \"{name_lower}=src.main:main\",\n        ],\n    }},\n)\n",
            "src/__init__.py": '"""\n{name}\n"""\n\n__version__ = "0.1.0"\n__author__ = "KaliRoot CLI"\n',
            "src/main.py": '#!/usr/bin/env python3\n"""\n{name} - Main Module\n"""\n\nimport logging\n\nlogger = logging.getLogger(__name__)\n\n\ndef main():\n    """Main entry point."""\n    print("Hello from {name}!")\n\n\nif __name__ == "__main__":\n    main()\n',
            "tests/__init__.py": "",
            "tests/test_main.py": "import pytest\n\n\ndef test_placeholder():\n    assert True\n"
        }
    },
    "audit": {
        "dirs": ["evidence", "reports", "tools", "configs", "logs", "screenshots"],
        "files": {
            "README.md": "# {name} - Security Audit\n\n## Scope\n\n## Timeline\n\n## Team\n",
            "scope.md": "# Audit Scope\n\n## In Scope\n- \n\n## Out of Scope\n- \n\n## Restrictions\n- ",
            "findings.md": "# Findings\n\n## 🔴 Critical\n\n## 🟠 High\n\n## 🟡 Medium\n\n## 🟢 Low\n\n## ℹ️ Informational\n",
            "checklist.md": "# Security Audit Checklist\n\n## Authentication\n- [ ] Password policy\n- [ ] MFA implementation\n- [ ] Session management\n\n## Authorization\n- [ ] Access controls\n- [ ] Privilege separation\n\n## Data Protection\n- [ ] Encryption at rest\n- [ ] Encryption in transit\n\n## Logging\n- [ ] Audit logs\n- [ ] Security events\n"
        }
    },
    "research": {
        "dirs": ["data", "analysis", "papers", "poc", "tools", "notes"],
        "files": {
            "README.md": "# {name} - Security Research\n\n## Hypothesis\n\n## Methodology\n\n## Findings\n",
            "hypothesis.md": "# Research Hypothesis\n\n## Background\n\n## Question\n\n## Expected Outcome\n",
            "methodology.md": "# Methodology\n\n## Approach\n\n## Tools\n\n## Data Collection\n",
            "references.md": "# References\n\n1. \n2. \n3. \n",
            "timeline.md": "# Research Timeline\n\n| Week | Task | Status |\n|------|------|--------|\n| 1 | Literature review | ⏳ |\n| 2 | Setup environment | ⏳ |\n| 3 | Data collection | ⏳ |\n| 4 | Analysis | ⏳ |\n| 5 | Documentation | ⏳ |\n"
        }
    },
    "ctf": {
        "dirs": ["challenges", "solved", "scripts", "notes", "tools"],
        "files": {
            "README.md": "# {name} - CTF Workspace\n\n## Event Info\n\n## Team\n\n## Progress\n",
            "challenges.md": "# Challenges\n\n## Web\n- [ ] Challenge 1\n\n## Pwn\n- [ ] Challenge 1\n\n## Crypto\n- [ ] Challenge 1\n\n## Reverse\n- [ ] Challenge 1\n\n## Forensics\n- [ ] Challenge 1\n",
            "flags.md": "# Flags\n\n| Challenge | Flag | Points | Solver |\n|-----------|------|--------|--------|\n",
            "scripts/template.py": "#!/usr/bin/env python3\n# CTF Challenge Solution\n\nfrom pwn import *\n\ncontext.log_level = 'debug'\n\ndef solve():\n    pass\n\nif __name__ == '__main__':\n    solve()\n"
        }
    },
    "scanner_tool": {
        "dirs": ["core", "modules", "utils", "reports", "data"],
        "files": {
            "main.py": "#!/usr/bin/env python3\n\"\"\"\n{name} - Advanced Security Scanner\n\"\"\"\nimport argparse\nfrom core.engine import ScannerEngine\n\ndef main():\n    parser = argparse.ArgumentParser(description='{description}')\n    parser.add_argument('target', help='Target to scan')\n    args = parser.parse_args()\n    engine = ScannerEngine(args.target)\n    engine.run()\n\nif __name__ == '__main__':\n    main()\n",
            "core/engine.py": "class ScannerEngine:\n    def __init__(self, target):\n        self.target = target\n    def run(self):\n        print(f'[*] Scanning {self.target}...')\n",
            "requirements.txt": "requests\nrich\nscapy\n",
            "README.md": "# {name}\n\n{description}\n\n## Installation\n`pip install -r requirements.txt`\n"
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# FILE MANAGER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class AgentFileManager:
    """
    Professional file management agent for creating and managing project files.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the file manager.
        """
        self.base_dir = base_dir or os.path.expanduser("~/kalirootcli_projects")
        self.current_project = None
        os.makedirs(self.base_dir, exist_ok=True)
    
    def set_project(self, project_name: str):
        """Set the active project context."""
        self.current_project = project_name
        
    def get_project_path(self) -> str:
        """Get current project path."""
        if not self.current_project:
            return self.base_dir
        return os.path.join(self.base_dir, self.current_project)

    def read_project_context(self) -> str:
        """Read all text files in current project to provide context to AI."""
        if not self.current_project:
            return ""
            
        context = []
        project_path = self.get_project_path()
        
        if not os.path.exists(project_path):
            return ""
            
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.startswith(".") or file.endswith((".pyc", ".git", ".png")):
                    continue
                    
                path = os.path.join(root, file)
                try:
                    rel_path = os.path.relpath(path, project_path)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Limit large files
                        if len(content) > 10000:
                            content = content[:10000] + "\n... (truncated)"
                        context.append(f"--- File: {rel_path} ---\n{content}\n")
                except Exception:
                    pass # Skip binary or unreadable
                    
        return "\n".join(context)

    def run_task(self, instruction: str) -> dict:
        """
        Execute a development task (Create or Edit) using AI.
        
        Args:
            instruction: User instruction
            
        Returns:
            Dict with success, message and type (created/edited)
        """
        from .api_client import api_client
        from .distro_detector import detector
        import json
        import re
        
        try:
            # 1. Get current code context if project exists
            current_code = self.read_project_context()
            
            project_context_prompt = ""
            if self.current_project:
                project_context_prompt = f"""
                ACTIVE PROJECT: {self.current_project}
                
                CURRENT CODEBASE STATE:
                {current_code}
                
                INSTRUCTION: Update the existing code or create new files based on: "{instruction}"
                """
            else:
                project_context_prompt = f"""
                NEW PROJECT REQUEST: "{instruction}"
                """

            # 2. Ask AI - Using Custom Delimiter Format (More Robust than JSON for code)
            query = f"""
            {project_context_prompt}
            
            ACT AS A SENIOR DEVELOPER.
            
            Return the response in this EXACT format (do not use JSON):
            
            PROJECT: {self.current_project or 'suggested_name_no_spaces'}
            SUMMARY: One line explanation of changes.
            
            --- filename.ext ---
            (Content of the file goes here)
            
            --- another_file.ext ---
            (Content of another file)
            
            RULES:
            1. Use '--- filename ---' as delimiter for every file.
            2. If modifying a file, return the FULL NEW CONTENT.
            3. Do not use markdown code blocks (```) for the delimiters, just plain text.
            """
            
            result = api_client.ai_query(query, environment=detector.get_system_info())
            
            if not result["success"]:
                return {"success": False, "error": result.get("error")}
                
            response_text = result["data"]["response"]
            
            # --- CUSTOM PARSER ---
            lines = response_text.splitlines()
            parsed_project = "generated_project"
            parsed_summary = "Changes applied"
            files_map = {}
            
            current_file = None
            current_content = []
            
            for line in lines:
                # Meta headers
                if line.startswith("PROJECT:") and not current_file:
                    parsed_project = line.replace("PROJECT:", "").strip()
                    continue
                if line.startswith("SUMMARY:") and not current_file:
                    parsed_summary = line.replace("SUMMARY:", "").strip()
                    continue
                    
                # File Delimiter Check (e.g. "--- main.py ---")
                # We look for lines starting with --- and ending with ---
                # But we must be careful not to catch separators inside code
                if line.strip().startswith("--- ") and line.strip().endswith(" ---"):
                    # Save previous file
                    if current_file:
                        files_map[current_file] = "\n".join(current_content).strip()
                    
                    # Start new file
                    # Extract filename: "--- main.py ---" -> "main.py"
                    current_file = line.strip()[4:-4].strip()
                    current_content = []
                    continue
                
                # If we are inside a file, append line
                if current_file:
                    current_content.append(line)
            
            # Save last file
            if current_file and current_content:
                files_map[current_file] = "\n".join(current_content).strip()
            
            if not files_map and not current_file:
                 # Fallback: maybe the AI wrapped it in ``` ???
                 # But let's assume it worked for now or return error
                 return {"success": False, "error": "No files parsed from AI response. Format error."}

            # 3. Apply Changes
            self.set_project(parsed_project)
            project_dir = self.get_project_path()
            os.makedirs(project_dir, exist_ok=True)
            
            files_created = []
            files_updated = []
            
            for filename, content in files_map.items():
                # Remove markdown code blocks if AI added them inside the file content
                if content.startswith("```"):
                    content = "\n".join(content.splitlines()[1:])
                if content.endswith("```"):
                    content = "\n".join(content.splitlines()[:-1])
                
                full_path = os.path.join(project_dir, filename)
                is_update = os.path.exists(full_path)
                
                # Ensure subdir
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
                if full_path.endswith(".py") or full_path.endswith(".sh"):
                    os.chmod(full_path, 0o755)
                    
                if is_update:
                    files_updated.append(filename)
                else:
                    files_created.append(filename)
            
            return {
                "success": True, 
                "project": parsed_project,
                "created": files_created, 
                "updated": files_updated,
                "summary": parsed_summary
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_from_template(
        self,
        template_name: str,
        name: str,
        description: str = "",
        directory: str = None,
        **extra_vars
    ) -> FileCreationResult:
        """
        Create a file from a predefined template.
        
        Args:
            template_name: Name of the template to use
            name: Name for the generated file/project
            description: Description to include
            directory: Target directory
            **extra_vars: Additional template variables
            
        Returns:
            FileCreationResult
        """
        if template_name not in TEMPLATES:
            available = ", ".join(TEMPLATES.keys())
            return FileCreationResult(
                success=False,
                error=f"Template '{template_name}' not found. Available: {available}"
            )
        
        template = TEMPLATES[template_name]
        
        # Build variables
        safe_name = name.replace(" ", "_").replace("-", "_")
        class_name = "".join(word.capitalize() for word in name.split())
        
        vars_dict = {
            "name": name,
            "name_lower": safe_name.lower(),
            "class_name": class_name,
            "description": description or f"Auto-generated {template_name}",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "objectives": "",
            "phases": ""
        }
        vars_dict.update(extra_vars)
        
        try:
            content = template.format(**vars_dict)
        except KeyError as e:
            return FileCreationResult(
                success=False,
                error=f"Missing template variable: {e}"
            )
        
        # Determine filename
        ext_map = {
            "python_script": ".py",
            "python_class": ".py",
            "bash_script": ".sh",
            "security_audit": "_audit.md",
            "project_plan": "_plan.md",
            "exploit_template": "_exploit.py"
        }
        
        ext = ext_map.get(template_name, ".txt")
        filename = f"{safe_name.lower()}{ext}"
        
        is_script = template_name in ["python_script", "python_class", "bash_script", "exploit_template"]
        
        return self.create_file(filename, content, directory, make_executable=is_script)
    
    def create_project_structure(
        self,
        project_name: str,
        project_type: Literal["pentest", "tool", "audit", "research", "ctf"] = "tool",
        description: str = ""
    ) -> Dict:
        """
        Create a complete project directory structure.
        
        Args:
            project_name: Name of the project
            project_type: Type of project structure
            description: Project description
            
        Returns:
            Dict with success status and project info
        """
        safe_name = project_name.lower().replace(" ", "_")
        project_dir = os.path.join(self.base_dir, safe_name)
        
        if project_type not in PROJECT_STRUCTURES:
            return {
                "success": False,
                "error": f"Unknown project type: {project_type}. Available: {list(PROJECT_STRUCTURES.keys())}"
            }
        
        try:
            structure = PROJECT_STRUCTURES[project_type]
            
            # Create project directory
            os.makedirs(project_dir, exist_ok=True)
            
            # Create subdirectories
            for d in structure["dirs"]:
                os.makedirs(os.path.join(project_dir, d), exist_ok=True)
            
            # Create files from templates
            for filename, content_template in structure["files"].items():
                filepath = os.path.join(project_dir, filename)
                
                # Create parent directory if needed
                parent = os.path.dirname(filepath)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                
                # Format content
                content = content_template.format(
                    name=project_name,
                    name_lower=safe_name,
                    description=description
                )
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
            
            logger.info(f"Created project: {project_dir}")
            
            return {
                "success": True,
                "path": project_dir,
                "message": f"✅ Proyecto '{project_name}' creado en: {project_dir}",
                "type": project_type,
                "structure": {
                    "directories": structure["dirs"],
                    "files": list(structure["files"].keys())
                }
            }
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_project_context(self, path: str = None) -> str:
        """
        Analyze the current directory context for AI.
        Returns a summary string of files and basic content.
        """
        target_path = path or os.getcwd()
        summary = [f"Directory: {target_path}\n"]
        
        try:
            # List files (respecting simple ignore list)
            ignore = {'.git', 'venv', '__pycache__', '.env', 'node_modules', '.idea', '.vscode'}
            
            for root, dirs, files in os.walk(target_path):
                # Filter dirs
                dirs[:] = [d for d in dirs if d not in ignore]
                
                rel_root = os.path.relpath(root, target_path)
                if rel_root == ".": 
                    rel_root = ""
                
                for f in files:
                    if f.startswith('.'): continue
                    
                    filepath = os.path.join(root, f)
                    rel_path = os.path.join(rel_root, f)
                    
                    # Add file to summary
                    summary.append(f"\nFile: {rel_path}")
                    
                    # Read content if text and small
                    try:
                        if os.path.getsize(filepath) < 5000:  # 5KB limit
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                                content = file_obj.read()
                                # Truncate if still too long for context
                                if len(content) > 2000:
                                    content = content[:2000] + "...[TRUNCATED]"
                                summary.append(f"Content:\n```\n{content}\n```")
                        else:
                            summary.append("(File too large for context)")
                    except Exception:
                        summary.append("(Binary or unreadable)")
                        
        except Exception as e:
            summary.append(f"Error scanning directory: {e}")
            
        return "\n".join(summary)

    def parse_natural_language_intent(self, prompt: str) -> Dict:
        """
        Parse a natural language prompt into an agent action.
        This is a simple heuristic parser; a real implementation would use LLM.
        """
        prompt = prompt.lower()
        
        # 1. Project Creation
        if "create" in prompt or "crear" in prompt or "new" in prompt or "nuevo" in prompt:
            # Detect type
            p_type = "tool"
            if "bot" in prompt or "telegram" in prompt: p_type = "tool"
            elif "pentest" in prompt: p_type = "pentest"
            elif "audit" in prompt or "auditoría" in prompt: p_type = "audit"
            elif "ctf" in prompt: p_type = "ctf"
            
            # Extract name (heuristic: last word or specific patterns)
            # This is naive but works for "create project my_tool"
            words = prompt.split()
            name = words[-1] if len(words) > 1 else "unnamed_project"
            
            return {
                "action": "create_project",
                "type": p_type,
                "name": name,
                "description": prompt
            }
            
        return {"action": "unknown"}

    def list_projects(self) -> List[Dict]:
        """List all projects in the base directory."""
        projects = []
        try:
            if not os.path.exists(self.base_dir):
                return []
                
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path):
                    # Detect project type
                    project_type = self._detect_project_type(item_path)
                    
                    projects.append({
                        "name": item,
                        "path": item_path,
                        "type": project_type,
                        "modified": datetime.fromtimestamp(
                            os.path.getmtime(item_path)
                        ).strftime("%Y-%m-%d %H:%M"),
                        "size": self._get_dir_size(item_path)
                    })
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
        
        return sorted(projects, key=lambda x: x["modified"], reverse=True)
    
    def _detect_project_type(self, path: str) -> str:
        """Detect project type based on directory structure."""
        contents = set(os.listdir(path))
        
        if "01_recon" in contents or "loot" in contents:
            return "pentest"
        elif "src" in contents and "tests" in contents:
            return "tool"
        elif "evidence" in contents or "findings.md" in contents:
            return "audit"
        elif "poc" in contents or "papers" in contents:
            return "research"
        elif "challenges" in contents:
            return "ctf"
        return "unknown"
    
    def _get_dir_size(self, path: str) -> str:
        """Get human-readable directory size."""
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except:
                    pass
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024:
                return f"{total:.1f} {unit}"
            total /= 1024
        return f"{total:.1f} TB"
    
    def delete_project(self, project_name: str, confirm: bool = False) -> Dict:
        """
        Delete a project directory.
        
        Args:
            project_name: Name of the project to delete
            confirm: Must be True to actually delete
            
        Returns:
            Dict with status
        """
        if not confirm:
            return {
                "success": False,
                "error": "Deletion requires explicit confirmation"
            }
        
        project_path = os.path.join(self.base_dir, project_name.lower().replace(" ", "_"))
        
        if not os.path.exists(project_path):
            return {"success": False, "error": "Project not found"}
        
        try:
            shutil.rmtree(project_path)
            return {
                "success": True,
                "message": f"Deleted project: {project_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT PLANNER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class ProjectPlanner:
    """
    Project planning and documentation agent.
    Creates structured plans and tracks progress.
    """
    
    def __init__(self, file_manager: AgentFileManager = None):
        self.file_manager = file_manager or AgentFileManager()
    
    def create_plan(
        self,
        name: str,
        description: str,
        objectives: List[str],
        phases: List[Dict] = None
    ) -> Dict:
        """
        Create a comprehensive project plan.
        
        Args:
            name: Project name
            description: Project description
            objectives: List of objectives
            phases: Optional custom phases
            
        Returns:
            Dict with creation status
        """
        plan = ProjectPlan(
            name=name,
            description=description,
            objectives=objectives,
            phases=phases
        )
        
        # Format objectives for template
        obj_text = "\n".join([f"- [ ] {o}" for o in objectives])
        
        # Format phases for template
        phases_text = ""
        for p in plan.phases:
            phases_text += f"### {p['name']}\n"
            phases_text += f"**Status:** ⏳ {p.get('status', 'pending').title()}\n\n"
            for t in p.get("tasks", []):
                phases_text += f"- [ ] {t}\n"
            phases_text += "\n"
        
        result = self.file_manager.create_from_template(
            "project_plan",
            name,
            description,
            objectives=obj_text,
            phases=phases_text
        )
        
        if result.success:
            # Also save JSON version for programmatic access
            json_path = result.path.replace(".md", ".json")
            try:
                with open(json_path, "w") as f:
                    json.dump(asdict(plan), f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error saving plan JSON: {e}")
        
        return {
            "success": result.success,
            "path": result.path,
            "message": result.message,
            "plan": asdict(plan)
        }
    
    def create_audit_report(
        self,
        name: str,
        description: str,
        directory: str = None
    ) -> Dict:
        """Create a security audit report template."""
        result = self.file_manager.create_from_template(
            "security_audit",
            name,
            description,
            directory=directory
        )
        
        return {
            "success": result.success,
            "path": result.path,
            "message": result.message
        }
    
    def list_plans(self) -> List[Dict]:
        """List all project plans."""
        plans = []
        
        try:
            for root, _, files in os.walk(self.file_manager.base_dir):
                for f in files:
                    if f.endswith("_plan.json"):
                        path = os.path.join(root, f)
                        try:
                            with open(path, "r") as file:
                                plan_data = json.load(file)
                                plans.append({
                                    "name": plan_data.get("name"),
                                    "path": path.replace(".json", ".md"),
                                    "status": plan_data.get("status"),
                                    "created": plan_data.get("created_at")
                                })
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error listing plans: {e}")
        
        return plans


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════════════════════════════

file_agent = AgentFileManager()
planner = ProjectPlanner(file_agent)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_script(name: str, description: str = "", script_type: str = "python") -> FileCreationResult:
    """Quick function to create a script."""
    template = "python_script" if script_type == "python" else "bash_script"
    return file_agent.create_from_template(template, name, description)

def create_project(name: str, project_type: str = "tool") -> Dict:
    """Quick function to create a project."""
    return file_agent.create_project_structure(name, project_type)

def create_plan(name: str, description: str, objectives: List[str]) -> Dict:
    """Quick function to create a project plan."""
    return planner.create_plan(name, description, objectives)

def list_templates() -> List[str]:
    """Get available templates."""
    return list(TEMPLATES.keys())

def list_project_types() -> List[str]:
    """Get available project types."""
    return list(PROJECT_STRUCTURES.keys())
