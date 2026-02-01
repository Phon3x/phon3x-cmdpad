#!/bin/bash
set -euo pipefail

# ==========================================================
# Phon3x-cmdPad Installer
# ==========================================================

# ---------------- Safety ----------------
if [[ ${EUID:-999} -eq 0 ]]; then
  echo "[!] Do NOT run this installer as root"
  exit 1
fi

if [[ -z "${HOME:-}" ]]; then
  echo "[!] HOME is not set. Aborting."
  exit 1
fi

# ---------------- Config ----------------
REPO_URL="https://github.com/Phon3x/phon3x-cmdpad.git"

PROJECT_DIR="$HOME/Phon3x-cmdPad"
SRC_DIR="$PROJECT_DIR/src"
VENV_DIR="$PROJECT_DIR/.venv"

CMDPAD_SCRIPT="$SRC_DIR/cmdpad/cmdpad.py"
REQ_FILE="$SRC_DIR/cmdpad/requirements.txt"

BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/cmdpad"

# ---------------- UI ----------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

step() { echo -e "${YELLOW}[+]${NC} $1"; }
ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
info() { echo -e "${BLUE}[i]${NC} $1"; }
err()  { echo -e "${RED}[!]${NC} $1"; }

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║              Phon3x-cmdPad Installer               ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ---------------- Distro detection ----------------
step "Detecting Linux distribution"
if [[ -f /etc/os-release ]]; then
  . /etc/os-release
else
  err "Cannot detect distro"
  exit 1
fi

# ---------------- System deps ----------------
step "Installing system dependencies"

case "$ID" in
  ubuntu|debian|linuxmint|kali)
    sudo apt update -y
    sudo apt install -y \
      git python3 python3-pip python3-venv \
      build-essential autoconf automake libtool \
      curl wget unzip
    ;;
  fedora)
    sudo dnf install -y \
      git python3 python3-pip \
      gcc gcc-c++ make autoconf automake libtool \
      curl wget unzip
    ;;
  arch)
    sudo pacman -Sy --noconfirm \
      git python python-pip base-devel \
      curl wget unzip
    ;;
  *)
    err "Unsupported distro: $ID"
    exit 1
    ;;
esac

ok "System dependencies ready"

# ---------------- Clone repo ----------------
step "Preparing project directory"
mkdir -p "$PROJECT_DIR"

if [[ -d "$SRC_DIR/.git" ]]; then
  info "Updating existing repository"
  git -C "$SRC_DIR" fetch --all --prune
  git -C "$SRC_DIR" reset --hard origin/main
else
  step "Cloning repository"
  rm -rf "$SRC_DIR"
  git clone --depth 1 "$REPO_URL" "$SRC_DIR"
fi

ok "Repository ready"

# ---------------- Validate files ----------------
[[ -f "$CMDPAD_SCRIPT" ]] || { err "cmdpad.py not found"; exit 1; }
[[ -f "$REQ_FILE" ]] || { err "requirements.txt not found"; exit 1; }

# ---------------- Virtual env ----------------
step "Setting up virtual environment"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
  ok "Virtual environment created"
else
  info "Virtual environment already exists"
fi

# ---------------- Python deps ----------------
step "Installing Python dependencies"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$REQ_FILE"
deactivate
ok "Python dependencies installed"

# ---------------- Launcher (UNBREAKABLE) ----------------
step "Installing global launcher"

mkdir -p "$BIN_DIR"
TMP_FILE="$(mktemp)"

cat > "$TMP_FILE" << EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" "$CMDPAD_SCRIPT" "\$@"
EOF

chmod +x "$TMP_FILE"
mv "$TMP_FILE" "$LAUNCHER"

ok "Command installed: cmdpad"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  info "~/.local/bin is not in PATH"
  info "Add with:"
  info "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
fi

# ---------------- systemd user service ----------------
read -p "Enable autostart via systemd user service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  step "Installing systemd user service"
  mkdir -p "$HOME/.config/systemd/user"

  cat > "$HOME/.config/systemd/user/cmdpad.service" << EOF
[Unit]
Description=Phon3x-cmdPad
After=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python $CMDPAD_SCRIPT
Restart=on-failure
Environment=QT_QPA_PLATFORM=wayland

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable cmdpad
  ok "Systemd service enabled"
fi

# ---------------- GNOME shortcut ----------------
if [[ "${XDG_CURRENT_DESKTOP:-}" == *"GNOME"* ]]; then
  read -p "Add GNOME shortcut Ctrl+Alt+C? (y/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    step "Configuring GNOME shortcut"

    BASE="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
    KEY="$BASE/cmdpad/"

    cur=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
    [[ "$cur" != *"$KEY"* ]] && \
      gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \
      "$(echo "$cur" | sed "s/]$/, '$KEY']/")"

    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEY name "'CmdPad'"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEY command "'cmdpad'"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEY binding "'<Control><Alt>c'"

    ok "Shortcut Ctrl+Alt+C added"
  fi
fi

# ---------------- Done ----------------
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}        INSTALLATION COMPLETE — CMDPAD READY        ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo "Run: cmdpad"
