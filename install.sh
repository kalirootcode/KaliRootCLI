#!/bin/bash
# ========================================
# KaliRoot CLI - Installation Script
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════╗"
echo "║       KALIROOT CLI INSTALLER           ║"
echo "║        Termux & Kali Linux             ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Detect environment
detect_environment() {
    if [ -d "/data/data/com.termux" ]; then
        echo -e "${GREEN}🔧 Detected: Termux${NC}"
        ENVIRONMENT="termux"
        INSTALL_DIR="$PREFIX/share/kalirootcli"
        BIN_DIR="$PREFIX/bin"
        DATA_DIR="$PREFIX/var/lib/kalirootcli"
        PIP_CMD="pip"
        PYTHON_CMD="python"
    elif [ -f "/etc/os-release" ] && grep -qi "kali" /etc/os-release; then
        echo -e "${GREEN}🔧 Detected: Kali Linux${NC}"
        ENVIRONMENT="kali"
        INSTALL_DIR="$HOME/.local/share/kalirootcli"
        BIN_DIR="$HOME/.local/bin"
        DATA_DIR="$HOME/.local/share/kalirootcli/data"
        PIP_CMD="pip3"
        PYTHON_CMD="python3"
    else
        echo -e "${YELLOW}🔧 Detected: Generic Linux${NC}"
        ENVIRONMENT="linux"
        INSTALL_DIR="$HOME/.local/share/kalirootcli"
        BIN_DIR="$HOME/.local/bin"
        DATA_DIR="$HOME/.local/share/kalirootcli/data"
        PIP_CMD="pip3"
        PYTHON_CMD="python3"
    fi
}

# Install Termux system packages (required for compiling Python libraries)
install_termux_deps() {
    if [ "$ENVIRONMENT" != "termux" ]; then
        return 0
    fi
    
    echo -e "${BLUE}📱 Installing Termux system packages...${NC}"
    echo -e "${YELLOW}   This may take a few minutes on first install.${NC}"
    
    # Update package lists
    pkg update -y 2>/dev/null || true
    
    # Essential build tools and libraries
    pkg install -y python clang make pkg-config 2>/dev/null || true
    
    # Libraries needed for common Python packages
    pkg install -y libxml2 libxslt libjpeg-turbo freetype libpng 2>/dev/null || true
    pkg install -y openssl libcrypt 2>/dev/null || true
    
    # Termux API for mobile-specific features (notifications, vibration, share)
    pkg install -y termux-api 2>/dev/null || true
    
    # Optional: Git for cloning repositories
    pkg install -y git 2>/dev/null || true
    
    echo -e "${GREEN}✅ Termux packages installed${NC}"
    echo ""
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    $PIP_CMD install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Create directories
create_directories() {
    echo -e "${BLUE}📁 Creating directories...${NC}"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DATA_DIR"
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Copy files
copy_files() {
    echo -e "${BLUE}📋 Copying files...${NC}"
    cp -r kalirootcli/* "$INSTALL_DIR/"
    echo -e "${GREEN}✅ Files copied to $INSTALL_DIR${NC}"
}

# Create launcher script
create_launcher() {
    echo -e "${BLUE}🚀 Creating launcher...${NC}"
    
    cat > "$BIN_DIR/kalirootcli" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
$PYTHON_CMD -m kalirootcli.main "\$@"
EOF
    
    chmod +x "$BIN_DIR/kalirootcli"
    echo -e "${GREEN}✅ Launcher created at $BIN_DIR/kalirootcli${NC}"
}

# Check if .env exists
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}"
        echo "⚠️  No .env file found!"
        echo "Please copy .env.template to .env and configure your API keys:"
        echo "  cp .env.template .env"
        echo "  nano .env  # or your favorite editor"
        echo -e "${NC}"
    else
        cp .env "$INSTALL_DIR/.env"
        echo -e "${GREEN}✅ Configuration copied${NC}"
    fi
}

# Add to PATH if needed
add_to_path() {
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "${YELLOW}⚠️  Please add $BIN_DIR to your PATH:${NC}"
        echo "  export PATH=\"\$PATH:$BIN_DIR\""
        echo ""
        echo "Add this line to your ~/.bashrc or ~/.zshrc for persistence."
    fi
}

# Main installation
main() {
    detect_environment
    echo ""
    
    install_termux_deps  # Install Termux system packages first
    install_dependencies
    create_directories
    copy_files
    create_launcher
    check_env
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo -e "Run with: ${CYAN}kalirootcli${NC}"
    echo -e "Or: ${CYAN}$PYTHON_CMD -m kalirootcli.main${NC}"
    echo ""
    
    add_to_path
}

# Run
main
