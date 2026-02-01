#!/bin/bash
set -euo pipefail

# ==========================================================
# Phon3x-cmdPad Uninstaller
# ==========================================================

# ---------------- Safety ----------------
if [[ ${EUID:-999} -eq 0 ]]; then
  echo "[!] Do NOT run this uninstaller as root"
  exit 1
fi

if [[ -z "${HOME:-}" ]]; then
  echo "[!] HOME is not set. Aborting."
  exit 1
fi

# ---------------- Config (MUST MATCH INSTALLER) ----------------
PROJECT_DIR="$HOME/Phon3x-cmdPad"
SRC_DIR="$PROJECT_DIR/src"
VENV_DIR="$PROJECT_DIR/.venv"

BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/cmdpad"

SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_DIR/cmdpad.service"

# ---------------- UI ----------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

step() { echo -e "${YELLOW}[+]${NC} $1"; }
ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
info() { echo -e "${BLUE}[i]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[!]${NC} $1"; }

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║              Phon3x-cmdPad Uninstaller             ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ---------------- systemd user service ----------------
if [[ -f "$SERVICE_FILE" ]]; then
  step "Removing systemd user service"

  systemctl --user stop cmdpad 2>/dev/null || true
  systemctl --user disable cmdpad 2>/dev/null || true
  systemctl --user daemon-reload

  rm -f "$SERVICE_FILE"
  ok "Systemd user service removed"
else
  info "No systemd user service found"
fi

# ---------------- GNOME shortcut ----------------
remove_gnome_shortcut() {
  BASE="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
  KEY="$BASE/cmdpad/"

  cur=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings)

  if [[ "$cur" == *"$KEY"* ]]; then
    step "Removing GNOME shortcut Ctrl+Alt+C"

    new=$(echo "$cur" | sed "s/, '$KEY'//; s/'$KEY', //; s/'$KEY'//")
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "$new"

    ok "GNOME shortcut removed"
  else
    info "GNOME shortcut not found"
  fi
}

if [[ "${XDG_CURRENT_DESKTOP:-}" == *"GNOME"* ]]; then
  remove_gnome_shortcut
fi

# ---------------- Launcher ----------------
if [[ -f "$LAUNCHER" ]]; then
  step "Removing launcher: $LAUNCHER"
  rm -f "$LAUNCHER"
  ok "Launcher removed"
else
  info "Launcher not found"
fi

# ---------------- Project directory ----------------
if [[ -d "$PROJECT_DIR" ]]; then
  echo ""
  read -p "Remove project directory ($PROJECT_DIR)? (y/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    step "Removing project directory"
    rm -rf "$PROJECT_DIR"
    ok "Project directory removed"
  else
    info "Project directory preserved"
  fi
else
  info "Project directory not found"
fi

# ---------------- PATH notice ----------------
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  info "~/.local/bin is not in PATH — no cleanup needed"
fi

# ---------------- Done ----------------
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           CMDPAD UNINSTALLED SUCCESSFULLY          ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
