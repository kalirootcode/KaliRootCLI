# KaliRoot CLI 🔒

Terminal-based cybersecurity assistant for **Termux** and **Kali Linux**.

## Features

- 🤖 **AI-Powered Assistant** - Groq-powered AI for cybersecurity questions
- 🔍 **Web Search** - Real-time internet search with DuckDuckGo
- 🕵️ **Agent Mode** - Auto-create scripts, projects, and security tools
- 🔐 **User Authentication** - Secure registration and login system
- 💎 **Free & Premium Tiers** - Subscription system with NowPayments
- 📱 **Multi-Platform** - Works on Termux (Android) and Kali Linux
- 🎨 **Beautiful CLI** - Colorful terminal interface with menus

## New in v2.0
- **Project Scaffolding**: Create Pentest, CTF, and Audit projects instantly
- **File Agent**: Generate Python/Bash scripts from templates
- **Planner**: Manage security audits and project timelines

## Quick Install (Smart Setup)

We recommend using the smart installer which detects your shell and sets up aliases automatically:

### 1-Line Install (Termux & Kali)
```bash
git clone https://github.com/yourusername/KaliRootCLI.git
cd KaliRootCLI

# Setup virtual environment (Recommended)
python3 -m venv venv
source venv/bin/activate

# Run Smart Installer
python3 install.py
```

### What `install.py` does:
1. Installs all required dependencies (AI, Web Search, Visualization)
2. Detects your shell (`bash` or `zsh`)
3. Adds aliases so you can use commands from anywhere:
   - `kaliroot` -> Launch main CLI
   - `kt-cli` -> Smart command wrapper

Don't forget to configure your API keys:
```bash
cp .env.template .env
nano .env
```

## Configuration

Copy `.env.template` to `.env` and fill in your credentials:

```bash
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
GROQ_API_KEY=your-groq-key
NOWPAYMENTS_API_KEY=your-nowpayments-key
IPN_SECRET_KEY=your-ipn-secret
```

## Usage

```bash
# Run the CLI
python -m kalirootcli.main

# Or after installation
kalirootcli
```

### 🤖 Agent Mode
Select **Option 2** in the main menu to access the Agent:

1. **Create Script**: Generate Python/Bash scripts from professional templates
2. **Create Project**: Scaffold complete directory structures for:
   - 🔓 **Pentest** (Recon, Scan, Exploit...)
   - 🛡️ **Audit** (Evidence, Reports...)
   - 🚩 **CTF** (Challenges, Solves...)
3. **Planner**: Create project plans and audit reports

> **Note for Termux Users**: Projects are saved in `~/kalirootcli_projects/` by default. You can access them using any file manager or terminal.

### 🧠 AI Console Commands
Inside the AI Console (Option 1):

- `/search <query>` - Search the web for real-time info
- `/news [topic]` - Get latest security news (default: cybersecurity)
- `/cve <id>` - Lookup CVE details (e.g., `/cve CVE-2024-3094`)
- `/websearch` - Toggle automatic web enrichment for queries

## Plans & Pricing

| Feature | Free | Premium ($10/month) |
|---------|------|---------------------|
| AI Queries | 5/day | Unlimited |
| Response Quality | Standard | Enhanced |
| Support | Community | Priority |
| Bonus Credits | - | +250/month |

## Database Setup

Run the migrations in your Supabase SQL editor:
```sql
-- See supabase_migrations.sql
```

## License

MIT License - Use responsibly for educational purposes only.

---

Made with 💀 by KaliRoot Team
