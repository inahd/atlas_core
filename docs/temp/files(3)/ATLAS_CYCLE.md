# Atlas Remediation Cycle

You are Claude Code running an automated remediation loop on the Atlas 330 system.
Working directory: `~/atlas_core/`
Kernel: `python kernel.py` → `localhost:5000`

## Your job

Read this file. Read the task queue. Pick the highest-priority incomplete task you can
complete without human input. Complete it. Verify it. Record what you did. Pick the next
task. Repeat until you hit a HUMAN_REQUIRED task or the queue is empty.

## Before every task

1. Read `docs/ATLAS_STATE_OF_THE_UNION.md` — current system state
2. Read `docs/ATLAS_CYCLE_LOG.md` — what has already been done this session
3. Check if the kernel is running: `curl -s localhost:5000/health`
   - If not running: `cd ~/atlas_core && python kernel.py &` then wait 3 seconds
4. Check git status: `git status --short`

## Task selection rules

- Work through tasks in Phase order (Phase 1 first, then 2, etc.)
- Within a phase, work in the order listed in STATE_OF_THE_UNION
- Skip any task marked HUMAN_REQUIRED
- Skip any task whose prerequisites are not yet done (check [x] status)
- If a task fails after two attempts, mark it HUMAN_REQUIRED and move on
- Never modify `datasets/relations/relations_resolved_canon.csv` without explicit instruction
- Never modify canonical entity counts (27 nakshatras, 9 grahas, 12 rashis)

## After every task

1. Run the verification check defined in the task prompt
2. If verification passes:
   - Mark the task `[x]` in `docs/ATLAS_STATE_OF_THE_UNION.md`
   - Append a line to `docs/ATLAS_CYCLE_LOG.md`
   - Commit: `git add -A && git commit -m "TASK-ID: one line summary"`
3. If verification fails after retry:
   - Mark task `[!] HUMAN_REQUIRED` in STATE_OF_THE_UNION
   - Log the failure in ATLAS_CYCLE_LOG.md
   - Move to next task

## Stop conditions

Stop and write a final summary to ATLAS_CYCLE_LOG.md if:
- All Phase 1 and Phase 2 tasks are complete or HUMAN_REQUIRED
- You have been running for more than 45 minutes
- You encounter a task that requires secrets, credentials, or hardware interaction
  you cannot verify (audio output, NPU hardware, external network)
- kernel.py crashes and won't restart

## Task prompts

Each task is fully described in `docs/prompts/queue/`. The filename matches the task ID.
Read the prompt file before executing the task.

## Start

Begin now. Read STATE_OF_THE_UNION, read CYCLE_LOG, pick your first task.
