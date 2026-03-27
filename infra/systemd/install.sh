#!/usr/bin/env bash
# install.sh — install Galley Archive systemd user service
#
# Usage:
#   bash infra/systemd/install.sh           # install galley.service (basic)
#   bash infra/systemd/install.sh proxy     # install galley-proxy.service (with nginx)
#
# Run from the repo root. Copies the unit file to ~/.config/systemd/user/
# and reloads the daemon. Does not enable or start the service automatically.
#
# After running this script:
#   systemctl --user enable galley          # start on login
#   systemctl --user start galley           # start now
#   loginctl enable-linger $USER            # start on boot without login (optional)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET_DIR="$HOME/.config/systemd/user"

MODE="${1:-}"

if [ "$MODE" = "proxy" ]; then
    UNIT_SRC="$SCRIPT_DIR/galley-proxy.service"
    UNIT_NAME="galley-proxy.service"
else
    UNIT_SRC="$SCRIPT_DIR/galley.service"
    UNIT_NAME="galley.service"
fi

# ── Check prerequisites ───────────────────────────────────────────────────────

if ! command -v docker >/dev/null 2>&1; then
    echo "Warning: docker not found in PATH — ensure Docker is installed before starting the service."
fi

if [ ! -f "$REPO_ROOT/.env" ]; then
    echo "Warning: .env not found at $REPO_ROOT/.env"
    echo "Run: cp .env.example .env   (from the repo root)"
fi

# ── Patch WorkingDirectory ────────────────────────────────────────────────────
# Systemd %h expands to $HOME at runtime, so the unit file should work as-is
# if the repo lives at ~/sevastolink-galley-archive.
# If not, warn the operator.

EXPECTED_PATH="$HOME/sevastolink-galley-archive"
if [ "$REPO_ROOT" != "$EXPECTED_PATH" ]; then
    echo ""
    echo "Note: repo is at:  $REPO_ROOT"
    echo "      unit expects: $EXPECTED_PATH  (via %h/sevastolink-galley-archive)"
    echo ""
    echo "The unit file uses WorkingDirectory=%h/sevastolink-galley-archive."
    echo "Edit ~/.config/systemd/user/$UNIT_NAME after install to set the correct path."
    echo "Change the WorkingDirectory and EnvironmentFile lines to use the actual path."
    echo ""
fi

# ── Install ───────────────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR"
cp "$UNIT_SRC" "$TARGET_DIR/$UNIT_NAME"
echo "Installed: $TARGET_DIR/$UNIT_NAME"

systemctl --user daemon-reload
echo "systemd user daemon reloaded."
echo ""
echo "Next steps:"
echo "  systemctl --user enable ${UNIT_NAME%.service}"
echo "  systemctl --user start  ${UNIT_NAME%.service}"
echo ""
echo "To start on boot without logging in:"
echo "  loginctl enable-linger \$USER"
