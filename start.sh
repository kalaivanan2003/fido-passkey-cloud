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
DB_NAME="1fidoclouddb"
DB_USER="root"

print_step() { echo -e "${YELLOW}$1${NC}"; }
print_ok()   { echo -e "${GREEN}✔ $1${NC}"; }
print_err()  { echo -e "${RED}✘ $1${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║   FIDO Cloud Authentication - Auto Installer    ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ──────────────────────────────────────────────────────────
# STEP 1: System Dependencies
# ──────────────────────────────────────────────────────────
print_step "[STEP 1/7] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-venv \
    mysql-server libmysqlclient-dev \
    git curl build-essential pkg-config
print_ok "System dependencies installed."

# ──────────────────────────────────────────────────────────
# STEP 2: Clone or Update Repository
# ──────────────────────────────────────────────────────────
print_step "[STEP 2/7] Setting up project repository..."
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
print_step "[STEP 3/7] Creating required folders..."
mkdir -p static/Qrcode static/upload static/Encrypt static/Decrypt
print_ok "Static folders created."

# ──────────────────────────────────────────────────────────
# STEP 4: MySQL Setup
# ──────────────────────────────────────────────────────────
print_step "[STEP 4/7] Configuring MySQL..."

# Start MySQL
sudo systemctl start mysql 2>/dev/null || sudo service mysql start 2>/dev/null || true
sudo systemctl enable mysql 2>/dev/null || true

# Disable validate_password & set empty root password
sudo mysql 2>/dev/null <<'MYSQL_SETUP'
UNINSTALL COMPONENT 'file://component_validate_password';
MYSQL_SETUP
# (ignore error if already uninstalled)

sudo mysql <<'MYSQL_AUTH'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
FLUSH PRIVILEGES;
MYSQL_AUTH

print_ok "MySQL root configured with empty password."

# ──────────────────────────────────────────────────────────
# STEP 5: Import Database & Fix Schema
# ──────────────────────────────────────────────────────────
print_step "[STEP 5/7] Setting up database schema..."

# Create database if not exists
mysql -u "$DB_USER" -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"

# Check if tables already exist
TABLE_COUNT=$(mysql -u "$DB_USER" "$DB_NAME" -se "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME';" 2>/dev/null || echo "0")

if [ "$TABLE_COUNT" -eq "0" ]; then
    echo "  Importing 1fidoclouddb.sql..."
    mysql -u "$DB_USER" "$DB_NAME" < 1fidoclouddb.sql
    print_ok "Database imported."
else
    echo "  Database already has tables — skipping import."
fi

# Always ensure face_encoding column exists (safe to run multiple times)
echo "  Ensuring face_encoding column exists in regtb..."
mysql -u "$DB_USER" "$DB_NAME" <<'FIX_SCHEMA'
ALTER TABLE regtb ADD COLUMN IF NOT EXISTS face_encoding LONGTEXT NULL;
FIX_SCHEMA
print_ok "Database schema is up to date."

# ──────────────────────────────────────────────────────────
# STEP 6: Python Virtual Environment & Packages
# ──────────────────────────────────────────────────────────
print_step "[STEP 6/7] Setting up Python environment..."
if [ ! -f "venv/bin/python" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_ok "Python packages installed."

# ──────────────────────────────────────────────────────────
# STEP 7: Patch App.py to listen on all interfaces
# ──────────────────────────────────────────────────────────
print_step "[STEP 7/7] Checking Flask host configuration..."
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
echo -e "${YELLOW}  ⚠  Ensure AWS Security Group has port 5000 open${NC}"
echo -e "${CYAN}  Press CTRL+C to stop the server.               ${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

source venv/bin/activate
python App.py
