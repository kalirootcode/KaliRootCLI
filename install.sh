#!/bin/bash

################################################################################
# KR-CLIDN Installer Script v1.0
# Compatible: Kali Linux, Debian, Ubuntu, Termux, macOS
# Usage: bash install.sh [options]
################################################################################

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables globales
INSTALL_DIR=""
CONFIG_DIR=""
BIN_DIR=""
REPO_URL="https://github.com/rk13Code/KaliRootCLI.git"
OS_TYPE=""
DISTRO=""
PYTHON_CMD="python3"
PIP_CMD="pip3"

################################################################################
# Funciones Utilitarias
################################################################################

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   KR-CLIDN INSTALLER v1.0                     ║"
    echo "║        Advanced Penetration Testing & OSINT Automation        ║"
    echo "║                                                               ║"
    echo "║              https://github.com/rk13Code/KaliRootCLI          ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_step() {
    echo -e "${CYAN}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_divider() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
}

# Detectar OS y configurar variables
detect_os() {
    print_step "Detectando sistema operativo..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        
        if [ -d "/data/data/com.termux" ]; then
            DISTRO="Termux"
            INSTALL_DIR="${PREFIX}/opt/kr-clidn"
            CONFIG_DIR="${HOME}/.config/kr-clidn"
            BIN_DIR="${PREFIX}/bin"
            PYTHON_CMD="python"
            PIP_CMD="pip"
        else
            if grep -qi "kali" /etc/os-release 2>/dev/null; then
                DISTRO="Kali Linux"
            elif grep -qi "debian" /etc/os-release 2>/dev/null; then
                DISTRO="Debian"
            elif grep -qi "ubuntu" /etc/os-release 2>/dev/null; then
                DISTRO="Ubuntu"
            else
                DISTRO="Linux Generic"
            fi
            
            INSTALL_DIR="${HOME}/.local/share/kr-clidn"
            CONFIG_DIR="${HOME}/.config/kr-clidn"
            BIN_DIR="${HOME}/.local/bin"
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        DISTRO="macOS"
        INSTALL_DIR="${HOME}/.local/share/kr-clidn"
        CONFIG_DIR="${HOME}/.config/kr-clidn"
        BIN_DIR="${HOME}/.local/bin"
        
    else
        print_error "Sistema operativo no soportado: $OSTYPE"
        return 1
    fi
    
    print_success "OS detectado: $DISTRO"
    return 0
}

# Verificar Python
check_python() {
    print_step "Verificando Python 3..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION encontrado"
        return 0
    else
        print_error "Python 3 no está instalado"
        return 1
    fi
}

# Instalar dependencias del sistema
install_system_deps() {
    print_divider
    echo -e "${CYAN}FASE 1: Instalación de Dependencias del Sistema${NC}"
    print_divider
    
    if [[ "$DISTRO" == "Termux" ]]; then
        print_step "Actualizando paquetes de Termux..."
        pkg update -y &>/dev/null
        pkg install -y python git pip curl openssl-dev &>/dev/null
        print_success "Dependencias de Termux instaladas"
        
    elif [[ "$DISTRO" == "Kali Linux" ]] || [[ "$DISTRO" == "Debian" ]] || [[ "$DISTRO" == "Ubuntu" ]]; then
        print_step "Actualizando gestor de paquetes..."
        
        if [ "$EUID" -eq 0 ]; then
            apt-get update -qq &>/dev/null
            apt-get install -y -qq python3 python3-pip python3-dev git curl wget build-essential libssl-dev libffi-dev &>/dev/null
        else
            sudo apt-get update -qq &>/dev/null
            sudo apt-get install -y -qq python3 python3-pip python3-dev git curl wget build-essential libssl-dev libffi-dev &>/dev/null
        fi
        
        print_success "Dependencias del sistema instaladas"
        
    elif [[ "$DISTRO" == "macOS" ]]; then
        print_warning "En macOS, asegúrate de tener Homebrew instalado"
        if command -v brew &> /dev/null; then
            brew install -q python3 git openssl &>/dev/null
            print_success "Dependencias instaladas"
        else
            print_error "Homebrew no encontrado. Instálalo desde https://brew.sh"
            return 1
        fi
    fi
}

# Crear directorios
create_directories() {
    print_step "Creando directorios..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$BIN_DIR"
    print_success "Directorios creados"
}

# Descargar repositorio
download_repository() {
    print_divider
    echo -e "${CYAN}FASE 2: Descargando KR-CLIDN${NC}"
    print_divider
    
    print_step "Descargando repositorio..."
    
    if command -v git &> /dev/null; then
        cd /tmp
        git clone --quiet --depth 1 "$REPO_URL" kr-clidn-temp 2>/dev/null
        if [ $? -eq 0 ]; then
            cp -r /tmp/kr-clidn-temp/kalirootcli/* "$INSTALL_DIR/" 2>/dev/null
            rm -rf /tmp/kr-clidn-temp
            print_success "Repositorio descargado exitosamente"
            return 0
        fi
    fi
    
    print_warning "No se pudo clonar con Git, intentando ZIP..."
    return 1
}

# Instalar dependencias de Python
install_python_deps() {
    print_divider
    echo -e "${CYAN}FASE 3: Instalando Dependencias de Python${NC}"
    print_divider
    
    print_step "Instalando paquetes Python..."
    
    # Lista de dependencias esenciales
    local deps=(
        "requests>=2.28.0"
        "supabase>=2.0.0"
        "python-dotenv>=0.21.0"
        "cryptography>=39.0.0"
        "beautifulsoup4>=4.11.0"
        "colorama>=0.4.6"
        "click>=8.1.0"
        "aiohttp>=3.8.0"
        "pydantic>=1.10.0"
    )
    
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel &>/dev/null
    
    for dep in "${deps[@]}"; do
        $PIP_CMD install -q "$dep" 2>/dev/null
    done
    
    print_success "Dependencias de Python instaladas"
}

# Configurar alias de comando
setup_command_alias() {
    print_divider
    echo -e "${CYAN}FASE 4: Configurando Comando${NC}"
    print_divider
    
    print_step "Creando alias 'kr-clidn'..."
    
    # Crear wrapper script
    cat > "$BIN_DIR/kr-clidn" << 'EOF'
#!/bin/bash
cd ~/.local/share/kr-clidn 2>/dev/null || cd $PREFIX/opt/kr-clidn 2>/dev/null || cd ~/.local/var/kr-clidn
python3 __main__.py "$@"
EOF
    
    chmod +x "$BIN_DIR/kr-clidn"
    
    # Agregar al PATH si es necesario
    if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
        print_warning "Agregando $BIN_DIR al PATH..."
        
        if [[ -f "$HOME/.bashrc" ]]; then
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
        fi
        
        if [[ -f "$HOME/.zshrc" ]]; then
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.zshrc"
        fi
    fi
    
    print_success "Comando 'kr-clidn' configurado"
}

# Crear archivo de configuración
setup_configuration() {
    print_divider
    echo -e "${CYAN}FASE 5: Configuración Inicial${NC}"
    print_divider
    
    print_step "Creando archivo de configuración..."
    
    cat > "$CONFIG_DIR/config.env" << 'EOF'
# KR-CLIDN Configuration
# Supabase Credentials
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_anon_key_here

# API Configuration
API_URL=https://api.kaliroot.com
API_TIMEOUT=30

# Application Settings
THEME=dark
LANGUAGE=es
DEBUG=false
EOF
    
    print_warning "Edita $CONFIG_DIR/config.env con tus credenciales"
    print_success "Archivo de configuración creado"
}

# Verificar instalación
verify_installation() {
    print_divider
    echo -e "${CYAN}FASE 6: Verificación de Instalación${NC}"
    print_divider
    
    print_step "Verificando archivos instalados..."
    
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/__main__.py" ]; then
        print_success "Instalación completada exitosamente"
        return 0
    else
        print_error "Verificación fallida"
        return 1
    fi
}

# Mostrar próximos pasos
show_next_steps() {
    print_divider
    echo -e "${GREEN}🎉 ¡INSTALACIÓN COMPLETADA!${NC}"
    print_divider
    
    echo ""
    echo -e "${CYAN}Próximos pasos:${NC}"
    echo ""
    echo "  1️⃣  Configura credenciales:"
    echo "     ${YELLOW}nano $CONFIG_DIR/config.env${NC}"
    echo ""
    echo "  2️⃣  Inicia KR-CLIDN:"
    echo "     ${YELLOW}kr-clidn${NC}"
    echo ""
    echo "  3️⃣  Ver ayuda:"
    echo "     ${YELLOW}kr-clidn --help${NC}"
    echo ""
    echo "  4️⃣  Documentación:"
    echo "     ${GREEN}https://github.com/rk13Code/KaliRootCLI/wiki${NC}"
    echo ""
    echo -e "${CYAN}Directorios instalados:${NC}"
    echo "  • Programa: ${YELLOW}$INSTALL_DIR${NC}"
    echo "  • Config: ${YELLOW}$CONFIG_DIR${NC}"
    echo "  • Comando: ${YELLOW}kr-clidn${NC}"
    echo ""
    echo -e "${GREEN}¡Happy Hacking! 🎯${NC}"
    echo ""
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    print_banner
    
    # Verificaciones previas
    detect_os || exit 1
    check_python || exit 1
    
    # Instalación
    install_system_deps
    create_directories
    download_repository || print_warning "Git no disponible, continuando sin descarga"
    install_python_deps
    setup_command_alias
    setup_configuration
    verify_installation || exit 1
    show_next_steps
    
    print_success "Instalador finalizado"
    echo ""
}

# Ejecutar script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
