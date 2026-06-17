#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# MapNotes — One-shot setup and launch script
# Works on: macOS, Ubuntu/Debian Linux
# Port: 8002 (leaves 8001 free for your other project)
# Usage:
#   chmod +x run.sh
#   ./run.sh              # full setup + launch
#   ./run.sh --reset      # stop any running instance, then relaunch (DB untouched)
#   ./run.sh --reset-withdb  # wipe DB + reseed, then launch
#   ./run.sh --stop       # kill the running server
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PORT=8002
VENV_DIR="venv"
PID_FILE=".mapnotes.pid"
LOG_FILE="mapnotes.log"
ADMIN_USER="anupamvm"
ADMIN_EMAIL="anupamvm@gmail.com"
ADMIN_PASS="Anupamvm1!"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}▶ $*${NC}"; }
success() { echo -e "${GREEN}✔ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠ $*${NC}"; }
error()   { echo -e "${RED}✖ $*${NC}" >&2; exit 1; }
header()  { echo -e "\n${BOLD}${GREEN}━━━ $* ━━━${NC}"; }

# ── Script location — always run from the project root ────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── --stop flag ───────────────────────────────────────────────────────────────
kill_port() {
    local pids
    pids=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        echo "$pids" | xargs kill 2>/dev/null || true
        success "Stopped all processes on port $PORT"
    else
        warn "Nothing running on port $PORT"
    fi
    rm -f "$PID_FILE"
}

if [[ "${1:-}" == "--stop" ]]; then
    kill_port
    exit 0
fi

# ── --reset flag (restart only, DB untouched) ────────────────────────────────
if [[ "${1:-}" == "--reset" ]]; then
    kill_port
    info "Restarting server (database untouched)..."
fi

# ── --reset-withdb flag (wipe DB + reseed) ────────────────────────────────────
RESET_DB=false
if [[ "${1:-}" == "--reset-withdb" ]]; then
    RESET_DB=true
    warn "Reset-withdb mode: database will be wiped and reseeded"
fi

# ── Detect OS ─────────────────────────────────────────────────────────────────
header "Detecting environment"
OS="$(uname -s)"
case "$OS" in
    Darwin)
        PLATFORM="mac"
        success "Platform: macOS"
        ;;
    Linux)
        PLATFORM="linux"
        # Detect distro
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            DISTRO="${ID:-linux}"
        else
            DISTRO="linux"
        fi
        success "Platform: Linux ($DISTRO)"
        ;;
    *)
        error "Unsupported OS: $OS. This script supports macOS and Ubuntu/Debian Linux."
        ;;
esac

# ── Check for port conflict ───────────────────────────────────────────────────
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    EXISTING_PIDS=$(lsof -ti tcp:$PORT 2>/dev/null | tr '\n' ' ' || true)
    warn "Port $PORT is already in use (PID: $EXISTING_PIDS)"
    warn "MapNotes may already be running. Use './run.sh --stop' first, or access https://localhost:$PORT"
    exit 0
fi

# ── Install system dependencies ───────────────────────────────────────────────
header "Checking system dependencies"

if [[ "$PLATFORM" == "linux" ]]; then
    # Disable CD-ROM apt source if present (causes update errors on servers)
    if grep -q "^deb cdrom:" /etc/apt/sources.list 2>/dev/null; then
        info "Disabling CD-ROM apt source..."
        sudo sed -i 's|^deb cdrom:|# deb cdrom:|g' /etc/apt/sources.list
    fi

    # Check if python3-venv is available
    if ! python3 -c "import venv" 2>/dev/null; then
        info "Installing python3-venv..."
        sudo apt-get update -qq 2>/dev/null || sudo apt-get update -qq --allow-unauthenticated 2>/dev/null || true
        sudo apt-get install -y -qq python3-venv python3-pip
    fi

    # Pillow needs these on Linux
    MISSING_PKGS=()
    for pkg in python3-dev libjpeg-dev zlib1g-dev; do
        if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            MISSING_PKGS+=("$pkg")
        fi
    done
    if [[ ${#MISSING_PKGS[@]} -gt 0 ]]; then
        info "Installing system packages: ${MISSING_PKGS[*]}"
        sudo apt-get update -qq 2>/dev/null || sudo apt-get update -qq --allow-unauthenticated 2>/dev/null || true
        sudo apt-get install -y -qq "${MISSING_PKGS[@]}"
    fi
fi

# ── Find Python 3.9+ ─────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 9 ]]; then
            PYTHON="$cmd"
            success "Python $VER found at $(command -v $cmd)"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo ""
    error "Python 3.9+ not found. Install it first:
  macOS:  brew install python@3.11
  Ubuntu: sudo apt-get install python3.11 python3.11-venv"
fi

# ── Create virtual environment ────────────────────────────────────────────────
header "Setting up virtual environment"

if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    success "Virtual environment created at ./$VENV_DIR/"
else
    success "Virtual environment already exists"
fi

# Activate
source "$VENV_DIR/bin/activate"
PYTHON_VENV="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# ── Install Python dependencies ───────────────────────────────────────────────
header "Installing Python dependencies"

# Upgrade pip silently
"$PIP" install --quiet --upgrade pip

# Install from requirements
if [[ -f "requirements/dev.txt" ]]; then
    info "Installing from requirements/dev.txt..."
    "$PIP" install --quiet -r requirements/dev.txt
    success "Dependencies installed"
else
    info "Installing from requirements/base.txt..."
    "$PIP" install --quiet -r requirements/base.txt
    success "Dependencies installed"
fi

header "Configuring environment"
success ".env loaded from repository"


# ── Handle --reset-withdb ─────────────────────────────────────────────────────
if [[ "$RESET_DB" == "true" ]]; then
    info "Wiping database..."
    rm -f db.sqlite3
    success "Database cleared"
fi

# ── Run Django setup ──────────────────────────────────────────────────────────
header "Setting up Django"

info "Running migrations..."
"$PYTHON_VENV" manage.py migrate --run-syncdb 2>&1 | grep -E "^(Applying|Running|OK|  )" || true
success "Migrations complete"

# Create superuser if none exists
USER_COUNT=$("$PYTHON_VENV" manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null || true)
USER_COUNT=$(echo "${USER_COUNT:-0}" | grep -E '^[0-9]+$' | tail -1 || echo "0")
USER_COUNT="${USER_COUNT:-0}"
if [[ "$USER_COUNT" -eq 0 ]]; then
    info "Creating admin superuser (username: $ADMIN_USER, password: $ADMIN_PASS)..."
    DJANGO_SUPERUSER_PASSWORD="$ADMIN_PASS" \
    "$PYTHON_VENV" manage.py createsuperuser \
        --username "$ADMIN_USER" \
        --email "$ADMIN_EMAIL" \
        --noinput 2>/dev/null || true
    success "Superuser created"
else
    success "Superuser already exists ($USER_COUNT user(s) found)"
fi

# Seed sample data if no properties exist
PROP_COUNT=$("$PYTHON_VENV" manage.py shell -c "
try:
    from apps.properties.models import Property
    print(Property.objects.count())
except:
    print(0)
" 2>/dev/null || true)
PROP_COUNT=$(echo "${PROP_COUNT:-0}" | grep -E '^[0-9]+$' | tail -1 || echo "0")
PROP_COUNT="${PROP_COUNT:-0}"

if [[ "$PROP_COUNT" -eq 0 ]]; then
    info "Seeding 25 sample Maharashtra properties..."
    "$PYTHON_VENV" manage.py seed_data 2>&1 | tail -3
    success "Sample data loaded"
else
    success "Database already has $PROP_COUNT properties — skipping seed"
fi

# Collect static files
info "Collecting static files..."
"$PYTHON_VENV" manage.py collectstatic --noinput --clear -v 0 2>/dev/null
success "Static files ready"

# ── Launch server ─────────────────────────────────────────────────────────────
header "Launching MapNotes on port $PORT"

# Kill any stale PID from a previous run
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    kill_port
fi

# Generate self-signed SSL cert if not present (enables HTTPS, avoids insecure form warnings)
if [[ ! -f "cert.crt" ]]; then
    info "Generating self-signed SSL certificate..."
    openssl req -x509 -newkey rsa:2048 -keyout cert.key -out cert.crt -days 3650 -nodes \
        -subj "/CN=mapnotes-local" 2>/dev/null
    success "SSL certificate generated (valid 10 years)"
fi

# Start in background with HTTPS via runserver_plus
"$PYTHON_VENV" manage.py runserver_plus --cert-file cert.crt --key-file cert.key 0.0.0.0:$PORT > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

# Wait and verify it started
sleep 3
if kill -0 "$SERVER_PID" 2>/dev/null; then
    # Check if port is actually listening
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}${BOLD}  MapNotes is running!${NC}"
        echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "  ${BOLD}URL:${NC}       https://localhost:$PORT"
        echo -e "  ${BOLD}Username:${NC}  $ADMIN_USER"
        echo -e "  ${BOLD}Password:${NC}  $ADMIN_PASS"
        echo -e "  ${BOLD}Admin:${NC}     https://localhost:$PORT/admin/"
        echo ""
        echo -e "  ${CYAN}Logs:${NC}      tail -f $LOG_FILE"
        echo -e "  ${CYAN}Stop:${NC}      ./run.sh --stop"
        echo -e "  ${CYAN}Restart:${NC}   ./run.sh --reset"
        echo -e "  ${CYAN}Reset DB:${NC}  ./run.sh --reset-withdb"
        echo ""
        if [[ "$PLATFORM" == "linux" ]]; then
            echo -e "  ${YELLOW}Firewall:${NC} If URLs above are unreachable: sudo ufw allow $PORT/tcp"
            echo ""
        fi
        echo -e "${GREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        error "Server started (PID $SERVER_PID) but port $PORT is not listening. Check logs: cat $LOG_FILE"
    fi
else
    error "Server failed to start. Check logs: cat $LOG_FILE"
fi
