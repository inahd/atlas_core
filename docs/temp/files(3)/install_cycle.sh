#!/bin/bash
# install_cycle.sh
#
# Installs Atlas 330 remediation cycle infrastructure into ~/atlas_core/
# Works regardless of where you run it from — uses its own location as the source.
#
# Usage:
#   bash install_cycle.sh
#   bash install_cycle.sh --atlas-root /path/to/atlas_core   # override destination

set -e

# ── Resolve source directory (where this script lives) ──────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Destination ──────────────────────────────────────────────────────────────
ATLAS_ROOT="$HOME/atlas_core"
for arg in "$@"; do
  case $arg in
    --atlas-root) ATLAS_ROOT="$2"; shift ;;
  esac
done

echo ""
echo "Atlas Cycle Installer"
echo "  Source : $SCRIPT_DIR"
echo "  Target : $ATLAS_ROOT"
echo ""

# ── Verify atlas_core exists ─────────────────────────────────────────────────
if [ ! -f "$ATLAS_ROOT/kernel.py" ]; then
  echo "ERROR: $ATLAS_ROOT/kernel.py not found."
  echo "Is atlas_core at $ATLAS_ROOT? Use --atlas-root to override."
  exit 1
fi
echo "✓ Found kernel.py at $ATLAS_ROOT"

# ── Create target directories ────────────────────────────────────────────────
mkdir -p "$ATLAS_ROOT/docs/prompts/queue"
mkdir -p "$ATLAS_ROOT/docs/prompts/done"
mkdir -p "$ATLAS_ROOT/docs/prompts/skipped"
mkdir -p "$ATLAS_ROOT/docs/prompts/backlog"
mkdir -p "$ATLAS_ROOT/docs/audit"
mkdir -p "$ATLAS_ROOT/config"
mkdir -p "$ATLAS_ROOT/scripts"
echo "✓ Directories created"

# ── Copy function with reporting ─────────────────────────────────────────────
install_file() {
  local src="$1"
  local dst="$2"
  if [ ! -f "$src" ]; then
    echo "  MISSING: $src"
    return 1
  fi
  cp "$src" "$dst"
  echo "  ✓ $(basename $src) → $dst"
}

# ── Core docs ────────────────────────────────────────────────────────────────
echo ""
echo "Installing docs..."
install_file "$SCRIPT_DIR/ATLAS_STATE_OF_THE_UNION.md"  "$ATLAS_ROOT/docs/ATLAS_STATE_OF_THE_UNION.md"
install_file "$SCRIPT_DIR/ATLAS_CYCLE.md"               "$ATLAS_ROOT/docs/ATLAS_CYCLE.md"

# Only install the log if it doesn't already exist (don't overwrite progress)
if [ ! -f "$ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md" ]; then
  install_file "$SCRIPT_DIR/ATLAS_CYCLE_LOG.md"         "$ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md"
else
  echo "  ↷ ATLAS_CYCLE_LOG.md already exists — keeping existing log"
fi

# ── Skill reference copies (local mirror — live skills are on claude.ai) ─────
echo ""
echo "Installing skill references..."
install_file "$SCRIPT_DIR/atlas-state-SKILL.md"         "$ATLAS_ROOT/docs/skills-atlas-state.md"
install_file "$SCRIPT_DIR/npu-integrator-SKILL.md"      "$ATLAS_ROOT/docs/skills-npu-integrator.md"

# ── Task prompts ─────────────────────────────────────────────────────────────
echo ""
echo "Installing task prompts..."
PROMPT_SRC="$SCRIPT_DIR/prompts/queue"
if [ ! -d "$PROMPT_SRC" ]; then
  echo "  ERROR: prompts/queue directory not found at $PROMPT_SRC"
  echo "  Expected structure:"
  echo "    $(dirname $SCRIPT_DIR)/"
  echo "      install_cycle.sh"
  echo "      ATLAS_CYCLE.md"
  echo "      ATLAS_STATE_OF_THE_UNION.md"
  echo "      prompts/queue/*.md"
  echo "      scripts/run_cycle.sh"
  exit 1
fi

for f in "$PROMPT_SRC"/*.md; do
  [ -f "$f" ] && install_file "$f" "$ATLAS_ROOT/docs/prompts/queue/$(basename $f)"
done

# ── Runner script ─────────────────────────────────────────────────────────────
echo ""
echo "Installing runner script..."
install_file "$SCRIPT_DIR/scripts/run_cycle.sh"         "$ATLAS_ROOT/scripts/run_cycle.sh"
chmod +x "$ATLAS_ROOT/scripts/run_cycle.sh"
echo "  ✓ run_cycle.sh marked executable"

# ── Copy audit outputs if present (from Claude Code audit run) ───────────────
AUDIT_FILES=(
  "engine_audit.md" "dataset_inventory.md" "AUDIT_SUMMARY.md"
  "route_audit.md" "corpus_audit.md" "relations_audit.md"
  "gap_analysis.md" "entity_coverage.md" "overlap_report.md"
  "consolidation_proposal.md" "environment_audit.md"
  "frontend_audit.md" "sound_audit.md"
)
audit_copied=0
for f in "${AUDIT_FILES[@]}"; do
  if [ -f "$SCRIPT_DIR/$f" ]; then
    cp "$SCRIPT_DIR/$f" "$ATLAS_ROOT/docs/audit/$f"
    audit_copied=$((audit_copied+1))
  fi
done
[ $audit_copied -gt 0 ] && echo "  ✓ Copied $audit_copied audit reports to docs/audit/"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " Installation complete"
echo "══════════════════════════════════════════════"
echo ""
echo "Files installed to $ATLAS_ROOT/docs/:"
find "$ATLAS_ROOT/docs" -maxdepth 3 -name "*.md" | sort | sed "s|$ATLAS_ROOT/||"
echo ""
echo "Task queue:"
ls "$ATLAS_ROOT/docs/prompts/queue/" | sort
echo ""
echo "Next steps:"
echo ""
echo "  1. Start the kernel (in one terminal):"
echo "     cd $ATLAS_ROOT && python kernel.py"
echo ""
echo "  2. Run a single task to test:"
echo "     bash $ATLAS_ROOT/scripts/run_cycle.sh --task DS-001"
echo ""
echo "  3. Run the full queue interactively (pauses between tasks):"
echo "     bash $ATLAS_ROOT/scripts/run_cycle.sh"
echo ""
echo "  4. Run automatically (no pauses, skips HUMAN_REQUIRED tasks):"
echo "     bash $ATLAS_ROOT/scripts/run_cycle.sh --auto"
echo ""
echo "  Monitor progress:"
echo "     tail -f $ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md"
