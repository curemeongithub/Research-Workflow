#!/usr/bin/env bash
# pipeline-logger.sh — Simplified hooks-based diagnostic logger for the Research Pipeline v2
# Called by .claude/settings.json hooks with the event name as $1
# Writes structured logs to diagnostics/
# v2: Removed unreliable CLAUDE_* env var reads — logs only what's knowable.

set -euo pipefail

EVENT="${1:-unknown}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
DIAGNOSTICS_DIR="$PROJECT_ROOT/diagnostics"
RUN_LOG="$DIAGNOSTICS_DIR/pipeline-run.log"
METRICS_FILE="$DIAGNOSTICS_DIR/phase-metrics.yaml"

# Ensure diagnostics dir exists
mkdir -p "$DIAGNOSTICS_DIR" 2>/dev/null || true

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

log_run() {
  echo "[$TIMESTAMP] $EVENT | $*" >> "$RUN_LOG"
}

# Read current phase from state file (returns "unknown" if not found)
current_phase() {
  if [ -f "$PROJECT_ROOT/pipeline-state.yaml" ]; then
    grep -E "^current_phase:" "$PROJECT_ROOT/pipeline-state.yaml" \
      | awk '{print $2}' | tr -d '[:space:]' 2>/dev/null || echo "unknown"
  else
    echo "unknown"
  fi
}

# ──────────────────────────────────────────────
# Event handlers
# ──────────────────────────────────────────────

case "$EVENT" in

  SubagentStart)
    PHASE=$(current_phase)
    log_run "SubagentStart phase=$PHASE"

    cat >> "$METRICS_FILE" << EOF
- phase: $PHASE
  started: "$TIMESTAMP"
  status: in_progress
EOF
    ;;

  SubagentStop)
    PHASE=$(current_phase)
    log_run "SubagentStop phase=$PHASE"

    cat >> "$METRICS_FILE" << EOF
  stopped: "$TIMESTAMP"
  status: stopped
EOF
    ;;

  PostToolUse)
    # Lightweight — just increment counter in run log
    log_run "ToolUse"
    ;;

  PreCompact)
    PHASE=$(current_phase)
    log_run "PreCompact phase=$PHASE — context compaction triggered"
    # Re-inject state file content into stdout so Claude picks it up
    if [ -f "$PROJECT_ROOT/pipeline-state.yaml" ]; then
      echo ""
      echo "=== AUTO-REINJECTED pipeline-state.yaml (PreCompact) ==="
      cat "$PROJECT_ROOT/pipeline-state.yaml"
      echo "=== END pipeline-state.yaml ==="
    fi
    ;;

  SessionStart)
    TRIGGER="${2:-fresh}"
    log_run "SessionStart trigger=$TRIGGER"

    if [ "$TRIGGER" = "compact" ]; then
      if [ -f "$PROJECT_ROOT/pipeline-state.yaml" ]; then
        echo ""
        echo "=== POST-COMPACT RESUME — pipeline-state.yaml ==="
        cat "$PROJECT_ROOT/pipeline-state.yaml"
        echo "=== END pipeline-state.yaml ==="
      else
        log_run "SessionStart compact — pipeline-state.yaml not found"
      fi
    fi
    ;;

  *)
    log_run "UnknownEvent event=$EVENT"
    ;;

esac

exit 0
