#!/bin/bash
# scripts/run_cycle.sh
#
# Atlas 330 automated remediation cycle runner.
# Runs Claude Code against each task prompt in order.
# Review output between tasks — do not run fully unattended on first use.
#
# Usage:
#   bash scripts/run_cycle.sh              # interactive — pauses between tasks
#   bash scripts/run_cycle.sh --auto       # automatic — runs until stop condition
#   bash scripts/run_cycle.sh --task DS-001  # run one specific task

set -e

ATLAS_ROOT="$HOME/atlas_core"
QUEUE_DIR="$ATLAS_ROOT/docs/prompts/queue"
DONE_DIR="$ATLAS_ROOT/docs/prompts/done"
SKIPPED_DIR="$ATLAS_ROOT/docs/prompts/skipped"
LOG="$ATLAS_ROOT/docs/ATLAS_CYCLE_LOG.md"
CYCLE_PROMPT="$ATLAS_ROOT/docs/ATLAS_CYCLE.md"
AUTO=false
SINGLE_TASK=""

mkdir -p "$DONE_DIR" "$SKIPPED_DIR"

# Parse args
for arg in "$@"; do
  case $arg in
    --auto) AUTO=true ;;
    --task) SINGLE_TASK="$2" ;;
  esac
done

log() {
  local msg="$(date '+%Y-%m-%d %H:%M') — $1"
  echo "$msg" >> "$LOG"
  echo "$msg"
}

check_kernel() {
  if curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1; then
    echo "kernel: running"
    return 0
  else
    echo "kernel: not running — starting..."
    cd "$ATLAS_ROOT"
    python kernel.py > /tmp/atlas_kernel.log 2>&1 &
    sleep 4
    if curl -s --max-time 3 localhost:5000/health > /dev/null 2>&1; then
      log "Kernel started automatically"
      return 0
    else
      log "WARN: kernel failed to start — continuing anyway"
      return 1
    fi
  fi
}

run_task() {
  local prompt_file="$1"
  local task_id="$(basename $prompt_file .md | sed 's/-.*$//')-$(basename $prompt_file .md | cut -d- -f2)"
  task_id="$(basename $prompt_file .md | grep -oE '^[A-Z]+-[0-9]+')"

  echo ""
  echo "════════════════════════════════════════"
  echo "  TASK: $task_id"
  echo "  FILE: $(basename $prompt_file)"
  echo "════════════════════════════════════════"

  if grep -q "HUMAN_REQUIRED" "$prompt_file"; then
    echo "→ Skipping: marked HUMAN_REQUIRED"
    log "[$task_id] SKIPPED — HUMAN_REQUIRED"
    cp "$prompt_file" "$SKIPPED_DIR/"
    return 0
  fi

  if [ "$AUTO" = false ]; then
    echo ""
    echo "Press ENTER to run this task, 's' to skip, 'q' to quit:"
    read -r choice
    case $choice in
      s|S) log "[$task_id] SKIPPED — user skip"; return 0 ;;
      q|Q) log "Cycle paused by user"; exit 0 ;;
    esac
  fi

  # Build the full prompt: cycle context + task-specific prompt
  local full_prompt=$(cat <<EOF
Read these files first:
1. ~/atlas_core/docs/ATLAS_STATE_OF_THE_UNION.md (system state)
2. ~/atlas_core/docs/ATLAS_CYCLE_LOG.md (what's already done)

Then execute this task:

$(cat "$prompt_file")

After completing the task:
1. Run the success check defined above
2. If it passes: append to ~/atlas_core/docs/ATLAS_CYCLE_LOG.md:
   "$(date '+%Y-%m-%d %H:%M') — [$task_id] DONE — [one line summary of what you did]"
3. If it fails: append:
   "$(date '+%Y-%m-%d %H:%M') — [$task_id] FAILED — [what went wrong]"
EOF
)

  echo "$full_prompt" | claude --print
  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    log "[$task_id] DONE — task runner reports success"
    mv "$prompt_file" "$DONE_DIR/"
  else
    log "[$task_id] FAILED — claude exited $exit_code"
    echo "Task failed. Mark as HUMAN_REQUIRED? (y/n)"
    if [ "$AUTO" = true ]; then
      log "[$task_id] HUMAN_REQUIRED — auto-mode, moving on"
    else
      read -r mark
      if [ "$mark" = "y" ]; then
        log "[$task_id] HUMAN_REQUIRED — marked by runner"
      fi
    fi
  fi
}

# Main loop
check_kernel

if [ -n "$SINGLE_TASK" ]; then
  # Run one specific task
  task_file=$(find "$QUEUE_DIR" -name "${SINGLE_TASK}*" | head -1)
  if [ -z "$task_file" ]; then
    echo "Task not found: $SINGLE_TASK"
    exit 1
  fi
  run_task "$task_file"
  exit 0
fi

# Run all tasks in queue, sorted by filename (phase order)
task_count=0
for prompt_file in $(ls "$QUEUE_DIR"/*.md 2>/dev/null | sort); do
  run_task "$prompt_file"
  task_count=$((task_count + 1))

  if [ "$AUTO" = true ] && [ $task_count -ge 20 ]; then
    log "Auto-mode: reached 20 tasks, stopping"
    break
  fi
done

echo ""
echo "════════════════════════════════════════"
echo "  Cycle complete. $task_count tasks processed."
echo "  See docs/ATLAS_CYCLE_LOG.md for results."
echo "════════════════════════════════════════"
log "Cycle complete — $task_count tasks processed"
