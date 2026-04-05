#!/usr/bin/env bash
# pipeline-logger.sh — Hooks-based diagnostic logger for the Research Pipeline
# Called by .claude/settings.json hooks with the event name as $1
# Writes structured logs to diagnostics/

set -euo pipefail

EVENT="${1:-unknown}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DIAGNOSTICS_DIR="${CLAUDE_PROJECT_DIR:-.}/diagnostics"
RUN_LOG="$DIAGNOSTICS_DIR/pipeline-run.log"
METRICS_FILE="$DIAGNOSTICS_DIR/phase-metrics.yaml"
TOOL_LOG="$DIAGNOSTICS_DIR/tool-calls.log"

# Ensure diagnostics dir exists (silent — do not pollute stdout)
mkdir -p "$DIAGNOSTICS_DIR" 2>/dev/null || true

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

log_run() {
  echo "[$TIMESTAMP] $EVENT | $*" >> "$RUN_LOG"
}

log_tool() {
  echo "[$TIMESTAMP] $*" >> "$TOOL_LOG"
}

# Read current phase from state file (returns 0 if not found)
current_phase() {
  if [ -f "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml" ]; then
    grep -E "^current_phase:" "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml" \
      | awk '{print $2}' | tr -d '[:space:]' 2>/dev/null || echo "0"
  else
    echo "0"
  fi
}

# ──────────────────────────────────────────────
# Event handlers
# ──────────────────────────────────────────────

case "$EVENT" in

  SubagentStart)
    PHASE=$(current_phase)
    AGENT_NAME="${CLAUDE_SUBAGENT_NAME:-unknown-agent}"
    log_run "SubagentStart phase=$PHASE agent=$AGENT_NAME"

    # Write phase start entry to metrics file
    cat >> "$METRICS_FILE" << EOF
- phase: $PHASE
  agent: $AGENT_NAME
  started: "$TIMESTAMP"
  status: in_progress
EOF
    ;;

  SubagentStop)
    PHASE=$(current_phase)
    AGENT_NAME="${CLAUDE_SUBAGENT_NAME:-unknown-agent}"
    EXIT_CODE="${CLAUDE_SUBAGENT_EXIT_CODE:-0}"
    log_run "SubagentStop phase=$PHASE agent=$AGENT_NAME exit_code=$EXIT_CODE"

    # Append stop event to metrics (a second entry — post-processing merges these)
    cat >> "$METRICS_FILE" << EOF
  stopped: "$TIMESTAMP"
  exit_code: $EXIT_CODE
EOF
    ;;

  PostToolUse)
    TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown-tool}"
    TOOL_EXIT="${CLAUDE_TOOL_EXIT_CODE:-0}"
    log_tool "tool=$TOOL_NAME exit=$TOOL_EXIT"
    ;;

  PreCompact)
    PHASE=$(current_phase)
    log_run "PreCompact phase=$PHASE — context compaction triggered"
    # Re-inject state file content into stdout so Claude picks it up
    if [ -f "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml" ]; then
      echo ""
      echo "=== AUTO-REINJECTED pipeline-state.yaml (PreCompact) ==="
      cat "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml"
      echo "=== END pipeline-state.yaml ==="
    fi
    ;;

  SessionStart)
    log_run "SessionStart"
    # If state file exists this is a resumed session — surface it
    if [ -f "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml" ]; then
      echo ""
      echo "=== RESUMED SESSION — pipeline-state.yaml ==="
      cat "${CLAUDE_PROJECT_DIR:-.}/pipeline-state.yaml"
      echo "=== END pipeline-state.yaml ==="
    fi
    ;;

  *)
    log_run "UnknownEvent event=$EVENT"
    ;;

esac

exit 0
