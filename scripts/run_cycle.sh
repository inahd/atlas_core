#!/bin/bash
# scripts/run_cycle.sh
#
# Atlas 330 automated remediation cycle runner.
#
# Usage:
#   bash scripts/run_cycle.sh              # interactive
#   bash scripts/run_cycle.sh --auto       # automatic, no pauses
#   bash scripts/run_cycle.sh --task DS-001  # single task

set -e

ATLAS_ROOT="$HOME/atlas_core"
AUTO=false
SINGLE_TASK=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --auto)       AUTO=true; shift ;;
    --task)       SINGLE_TASK="$2"; shift 2 ;;
    --atlas-root) ATLAS_ROOT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

QUEUE_DIR="$ATLAS_ROOT/docs/prompts/queue"
DONE_DIR="$ATLAS_ROOT/docs/prompts/done"
SKIPPED_DIR="$ATLAS_ROOT/docs/prompts/skipped"
LOG="$ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md"

mkdir -p "$DONE_DIR" "$SKIPPED_DIR"

log() {
  local msg="$(date '+%Y-%m-%d %H:%M') — $1"
  echo "$msg" | tee -a "$LOG"
}

check_kernel() {
  if curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1; then
    echo "kernel: running"
  else
    echo "kernel: not running — starting in background..."
    ( cd "$ATLAS_ROOT" && python kernel.py > /tmp/atlas_kernel.log 2>&1 ) &
    sleep 4
    curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1 \
      && log "Kernel started" \
      || log "WARN: kernel not responding — continuing anyway"
  fi
}

run_task() {
  local prompt_file="$1"
  local task_id
  task_id="$(basename "$prompt_file" .md | grep -oE '^[A-Z]+-[0-9]+')"

  echo ""
  echo "════════════════════════════════════════"
  echo "  TASK: $task_id"
  echo "  FILE: $(basename $prompt_file)"
  echo "════════════════════════════════════════"

  if [ "$AUTO" = false ]; then
    echo "Press ENTER to run, 's' to skip, 'q' to quit:"
    read -r choice
    case $choice in
      s|S) log "[$task_id] SKIPPED — user"; return 0 ;;
      q|Q) log "Cycle paused by user"; exit 0 ;;
    esac
  fi

  # Write full prompt to temp file — avoids stdin pipe issues
  local tmp_prompt
  tmp_prompt="$(mktemp /tmp/atlas_prompt_XXXXXX.md)"

  cat > "$tmp_prompt" << EOF
Working directory: $ATLAS_ROOT
You have full permission to read and write any file under $ATLAS_ROOT.
Do not ask for permission — just proceed.

Read these two files first before doing anything else:
1. $ATLAS_ROOT/docs/ATLAS_STATE_OF_THE_UNION.md
2. $ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md

Then execute this task:

$(cat "$prompt_file")

After completing the task:
1. Run the success check defined in the task above
2. If it passes, append to $LOG:
   "$(date '+%Y-%m-%d %H:%M') — [$task_id] DONE — [one line summary]"
3. If it fails, append:
   "$(date '+%Y-%m-%d %H:%M') — [$task_id] FAILED — [reason]"
EOF

  # Run from atlas_core dir; --dangerously-skip-permissions skips all approval gates
  ( cd "$ATLAS_ROOT" && claude --dangerously-skip-permissions --print < "$tmp_prompt" )
  local exit_code=$?
  rm -f "$tmp_prompt"

  if [ $exit_code -eq 0 ]; then
    log "[$task_id] runner: claude exited 0"
    mv "$prompt_file" "$DONE_DIR/"
  else
    log "[$task_id] FAILED — claude exited $exit_code"
    if [ "$AUTO" = true ]; then
      log "[$task_id] HUMAN_REQUIRED — auto-mode skipping"
      mv "$prompt_file" "$SKIPPED_DIR/"
    else
      echo "Task failed. Move to skipped and continue? (y/n)"
      read -r mark
      [ "$mark" = "y" ] && mv "$prompt_file" "$SKIPPED_DIR/" && log "[$task_id] HUMAN_REQUIRED"
    fi
  fi
}

# ── Main ─────────────────────────────────────────────────────────────────────
check_kernel

if [ -n "$SINGLE_TASK" ]; then
  task_file=$(find "$QUEUE_DIR" -name "${SINGLE_TASK}*" | head -1)
  if [ -z "$task_file" ]; then
    echo "Task not found: $SINGLE_TASK"
    echo "Queue:"; ls "$QUEUE_DIR/" | sed 's/^/  /'
    exit 1
  fi
  run_task "$task_file"
  exit 0
fi

task_count=0
for prompt_file in $(ls "$QUEUE_DIR"/*.md 2>/dev/null | sort); do
  run_task "$prompt_file"
  task_count=$((task_count + 1))
  [ "$AUTO" = true ] && [ $task_count -ge 100 ] && { log "Auto: 20 task limit"; break; }
done

echo ""
echo "════════════════════════════════════════"
echo "  Done. $task_count tasks. Log: $LOG"
echo "════════════════════════════════════════"
log "Cycle complete — $task_count tasks"
