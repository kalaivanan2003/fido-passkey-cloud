#!/bin/bash

# ============================================================
#   FIDO Cloud Authentication - Full Ubuntu Auto-Setup
#   Repo: https://github.com/kalaivanan2003/FIDO-passkey.git
#   Run: chmod +x start.sh && ./start.sh
# ============================================================

set -e

# ── Colors ─────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_URL="https://github.com/kalaivanan2003/FIDO-passkey.git"
PROJECT_DIR="$HOME/projects/FIDO-passkey"

print_step() { echo -e "${YELLOW}$1${NC}"; }
print_ok()   { echo -e "${GREEN}✔ $1${NC}"; }
print_err()  { echo -e "${RED}✘ $1${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║   FIDO Cloud Authentication - Auto Installer    ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ──────────────────────────────────────────────────────────
# STEP 1: System Dependencies  (no MySQL needed — uses SQLite)
# ──────────────────────────────────────────────────────────
print_step "[STEP 1/6] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-venv \
    git curl build-essential pkg-config
print_ok "System dependencies installed."

# ──────────────────────────────────────────────────────────
# STEP 2: Clone or Update Repository
# ──────────────────────────────────────────────────────────
print_step "[STEP 2/6] Setting up project repository..."
mkdir -p "$HOME/projects"
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "  Repository exists — pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "  Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi
print_ok "Repository ready at $PROJECT_DIR"

# ──────────────────────────────────────────────────────────
# STEP 3: Create Required Static Folders
# ──────────────────────────────────────────────────────────
print_step "[STEP 3/6] Creating required folders..."
mkdir -p static/Qrcode static/upload static/Encrypt static/Decrypt
print_ok "Static folders created."

# ──────────────────────────────────────────────────────────
# STEP 4: Python Virtual Environment & Packages
# ──────────────────────────────────────────────────────────
print_step "[STEP 4/6] Setting up Python environment..."
if [ ! -f "venv/bin/python" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_ok "Python packages installed."

# ──────────────────────────────────────────────────────────
# STEP 5: Initialise SQLite Database (safe to re-run)
# ──────────────────────────────────────────────────────────
print_step "[STEP 5/6] Initialising SQLite database..."
python init_db.py
print_ok "SQLite database ready (fidoclouddb.sqlite)."

# ──────────────────────────────────────────────────────────
# STEP 6: Check Flask host configuration
# ──────────────────────────────────────────────────────────
print_step "[STEP 6/6] Checking Flask host configuration..."
if grep -q "app.run(debug=True)" App.py; then
    sed -i "s/app.run(debug=True)/app.run(host='0.0.0.0', port=5000, debug=True)/" App.py
    print_ok "App.py patched to listen on 0.0.0.0:5000"
else
    print_ok "App.py host config already set."
fi

# ──────────────────────────────────────────────────────────
# Launch Flask
# ──────────────────────────────────────────────────────────
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || curl -s https://api.ipify.org 2>/dev/null || echo "your-public-ip")
PRIVATE_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✔ All setup complete! Server is starting...    ${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
echo -e "${GREEN}  🌐 Local:    http://localhost:5000              ${NC}"
echo -e "${GREEN}  🔒 Private:  http://$PRIVATE_IP:5000         ${NC}"
echo -e "${GREEN}  🌍 Public:   http://$PUBLIC_IP:5000           ${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
echo -e "${YELLOW}  ⚠  Ensure port 5000 is open in your firewall   ${NC}"
echo -e "${CYAN}  Press CTRL+C to stop the server.               ${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

source venv/bin/activate
python App.py
