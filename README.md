# KaliRoot CLI 🔒

Terminal-based cybersecurity assistant for **Termux** and **Kali Linux**.

## Features

- 🤖 **AI-Powered Assistant** - Groq-powered AI for cybersecurity questions
- 🔐 **User Authentication** - Secure registration and login system
- 💎 **Free & Premium Tiers** - Subscription system with NowPayments
- 📱 **Multi-Platform** - Works on Termux (Android) and Kali Linux
- 🎨 **Beautiful CLI** - Colorful terminal interface with menus

## Quick Install

### Termux (Android)
```bash
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/yourusername/KaliRootCLI.git
cd KaliRootCLI
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
python -m kalirootcli.main
```

### Kali Linux
```bash
sudo apt update && sudo apt install python3 python3-pip git
git clone https://github.com/yourusername/KaliRootCLI.git
cd KaliRootCLI
pip3 install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
python3 -m kalirootcli.main
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
