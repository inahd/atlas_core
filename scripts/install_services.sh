#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Install Atlas systemd user services
#
# Services:
#   atlas-sc.service       SuperCollider server (scsynth via pw-jack)
#   atlas-sclang.service   SC language (loads atlas_synth.scd)
#   atlas-porter.service   Audio connection watchdog
#   atlas-om.service       Tanpura drone (om.py → pw-cat → MOTU)
#   atlas-kernel.service   Flask API (kernel.py port 5000)
#   atlas-ngrok.service    Public tunnel
#   atlas.target           All of the above
#
# Usage:
#   ./scripts/install_services.sh
#   systemctl --user start atlas.target
# ═══════════════════════════════════════════════════════════

set -e

ATLAS="$(cd "$(dirname "$0")/.." && pwd)"
SYSTEMD_USER="${HOME}/.config/systemd/user"

echo "Atlas: $ATLAS"
echo "Target: $SYSTEMD_USER"

mkdir -p "$SYSTEMD_USER"

# Copy all atlas-* service files and target
for f in "$ATLAS/systemd/atlas-"*.service "$ATLAS/systemd/atlas.target"; do
    if [ -f "$f" ]; then
        cp "$f" "$SYSTEMD_USER/"
        echo "  copied: $(basename "$f")"
    fi
done

# Reload systemd daemon
systemctl --user daemon-reload
echo "  daemon reloaded"

# Enable all services
for unit in \
    atlas-sc.service \
    atlas-sclang.service \
    atlas-porter.service \
    atlas-om.service \
    atlas-kernel.service \
    atlas-ngrok.service \
    atlas.target \
; do
    systemctl --user enable "$unit" 2>/dev/null && echo "  enabled: $unit" || echo "  skip: $unit"
done

echo ""
echo "✦ Atlas services installed"
echo ""
echo "  start:   systemctl --user start atlas.target"
echo "  stop:    systemctl --user stop atlas.target"
echo "  status:  systemctl --user status 'atlas-*'"
echo "  logs:    journalctl --user -u 'atlas-*' -f"
echo ""
echo "  For auto-start on boot (without login):"
echo "    loginctl enable-linger $USER"
echo ""
