#!/bin/bash
# Jarvis AI One-Click Installer for Unix/Linux/macOS
# This script provides automated installation for non-technical users

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
JARVIS_VERSION="2.0.0"
INSTALL_DIR="$HOME/jarvis-ai"
PYTHON_MIN_VERSION="3.8"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                    Jarvis AI Installer                    ║"
    echo "║          Privacy-first AI Development Assistant           ║"
    echo "║                     Version $JARVIS_VERSION                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_python_version() {
    if check_command python3; then
        PYTHON_CMD="python3"
    elif check_command python; then
        PYTHON_CMD="python"
    else
        return 1
    fi

    version=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    major=$(echo $version | cut -d. -f1)
    minor=$(echo $version | cut -d. -f2)
    
    if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
        return 0
    else
        return 1
    fi
}

install_python() {
    print_step "Python $PYTHON_MIN_VERSION+ not found. Installing Python..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if check_command brew; then
            brew install python@3.11
        else
            print_error "Homebrew not found. Please install Python manually from https://python.org"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if check_command apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif check_command yum; then
            sudo yum install -y python3 python3-pip
        elif check_command dnf; then
            sudo dnf install -y python3 python3-pip
        else
            print_error "Package manager not found. Please install Python manually."
            exit 1
        fi
    else
        print_error "Unsupported operating system. Please install Python manually."
        exit 1
    fi
}

install_git() {
    print_step "Git not found. Installing Git..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if check_command brew; then
            brew install git
        else
            print_error "Please install Git manually from https://git-scm.com"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if check_command apt-get; then
            sudo apt-get install -y git
        elif check_command yum; then
            sudo yum install -y git
        elif check_command dnf; then
            sudo dnf install -y git
        fi
    fi
}

main() {
    print_header
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please don't run this script as root/sudo"
        exit 1
    fi
    
    # System checks
    print_step "Checking system requirements..."
    
    # Check Python
    if ! check_python_version; then
        install_python
    fi
    print_success "Python check passed"
    
    # Check Git
    if ! check_command git; then
        install_git
    fi
    print_success "Git check passed"
    
    # Check pip
    if ! check_command pip3 && ! check_command pip; then
        print_error "pip not found. Please install pip manually."
        exit 1
    fi
    print_success "pip check passed"
    
    # Create installation directory
    print_step "Creating installation directory at $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone repository
    print_step "Downloading Jarvis AI..."
    if [ -d ".git" ]; then
        git pull origin main
    else
        git clone "$GITHUB_REPO_URL" .
    fi
    print_success "Download completed"
    
    # Create virtual environment
    print_step "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    print_success "Virtual environment created"
    
    # Upgrade pip
    print_step "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Install Jarvis AI
    print_step "Installing Jarvis AI and dependencies..."
    pip install -e .
    print_success "Installation completed"
    
    # Initialize configuration
    print_step "Initializing configuration..."
    jarvis config --init
    print_success "Configuration initialized"
    
    # Create launcher script
    print_step "Creating launcher script..."
cat > "$INSTALL_DIR/start-jarvis.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
jarvis run "$@"
EOF
    chmod +x "$INSTALL_DIR/start-jarvis.sh"
    
    # Create desktop entry (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        mkdir -p "$HOME/.local/share/applications"
        cat > "$HOME/.local/share/applications/jarvis-ai.desktop" << EOF
[Desktop Entry]
Name=Jarvis AI
Comment=Privacy-first AI Development Assistant
Exec=$INSTALL_DIR/start-jarvis.sh
Icon=$INSTALL_DIR/icon.png
Terminal=true
Type=Application
Categories=Development;
EOF
        print_success "Desktop shortcut created"
    fi
    
    # Installation complete
    echo
    echo -e "${GREEN}🎉 Jarvis AI installation completed successfully!${NC}"
    echo
    echo "Getting Started:"
    echo "1. To start Jarvis AI:"
    echo "   cd $INSTALL_DIR && ./start-jarvis.sh"
    echo "   or"
    echo "   cd $INSTALL_DIR && source venv/bin/activate && jarvis run \"<objective>\""
    echo
    echo "2. Open your browser to: http://localhost:8501"
    echo
    echo "3. To update Jarvis AI in the future:"
    echo "   cd $INSTALL_DIR && git pull && pip install -e ."
    echo
    echo "Configuration file: $INSTALL_DIR/config/config.yaml"
    echo "Documentation: https://github.com/jimmyjdejesus-cmyk/Jarvis_AI/docs"
    echo
}

# Run installer
main "$@"