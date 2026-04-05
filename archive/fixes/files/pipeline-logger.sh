#!/usr/bin/env bash
# pipeline-logger.sh — Hooks-based diagnostic logger for the Research Pipeline
# Called by .claude/settings.json hooks with the event name as $1
# Writes structured logs to diagnostics/

set -euo pipefail

EVENT="${1:-unknown}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
DIAGNOSTICS_DIR="$PROJECT_ROOT/diagnostics"
RUN_LOG="$DIAGNOSTICS_DIR/pipeline-run.log"
METRICS_FILE="$DIAGNOSTICS_DIR/phase-metrics.yaml"
TOOL_LOG="$DIAGNOSTICS_DIR/tool-calls.log"
ENV_PROBE_FILE="$DIAGNOSTICS_DIR/hook-env-probe.log"

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

# Read current phase from state file (returns "unknown" if not found)
current_phase() {
  if [ -f "$PROJECT_ROOT/pipeline-state.yaml" ]; then
    grep -E "^current_phase:" "$PROJECT_ROOT/pipeline-state.yaml" \
      | awk '{print $2}' | tr -d '[:space:]' 2>/dev/null || echo "unknown"
  else
    echo "unknown"
  fi
}

# Safe read of an env var: prints its value if set and non-empty,
# otherwise prints the fallback and writes a one-time warning to the probe log.
safe_env() {
  local var_name="$1"
  local fallback="$2"
  local value="${!var_name:-}"
  if [ -n "$value" ]; then
    echo "$value"
  else
    # Write a warning only once per var per session (guard with grep)
    if ! grep -q "MISSING:$var_name" "$ENV_PROBE_FILE" 2>/dev/null; then
      echo "[$TIMESTAMP] MISSING:$var_name — Claude Code did not set this env var in the hook context. Falling back to '$fallback'. Check Claude Code hook documentation for available variables." >> "$ENV_PROBE_FILE"
    fi
    echo "$fallback"
  fi
}

# ──────────────────────────────────────────────
# One-time environment probe (runs on first hook call per session)
# ──────────────────────────────────────────────
probe_env_once() {
  # Only probe if the file doesn't exist yet (first hook call this session)
  if [ -f "$ENV_PROBE_FILE" ]; then
    return
  fi
  {
    echo "[$TIMESTAMP] === Hook Environment Probe ==="
    echo "[$TIMESTAMP] Script called as: $0 $*"
    echo "[$TIMESTAMP] CLAUDE_PROJECT_DIR=${CLAUDE_PROJECT_DIR:-<unset>}"
    echo "[$TIMESTAMP] CLAUDE_SUBAGENT_NAME=${CLAUDE_SUBAGENT_NAME:-<unset>}"
    echo "[$TIMESTAMP] CLAUDE_TOOL_NAME=${CLAUDE_TOOL_NAME:-<unset>}"
    echo "[$TIMESTAMP] CLAUDE_TOOL_EXIT_CODE=${CLAUDE_TOOL_EXIT_CODE:-<unset>}"
    echo "[$TIMESTAMP] CLAUDE_SUBAGENT_EXIT_CODE=${CLAUDE_SUBAGENT_EXIT_CODE:-<unset>}"
    # Dump all CLAUDE_* vars that ARE set, so we can discover undocumented ones
    echo "[$TIMESTAMP] All CLAUDE_* env vars present:"
    env | grep "^CLAUDE_" | sed "s/^/[$TIMESTAMP]   /" || echo "[$TIMESTAMP]   (none)"
    echo "[$TIMESTAMP] === End Probe ==="
  } >> "$ENV_PROBE_FILE"
}

probe_env_once "$@"

# ──────────────────────────────────────────────
# Event handlers
# ──────────────────────────────────────────────

case "$EVENT" in

  SubagentStart)
    PHASE=$(current_phase)
    # Use safe_env: if CLAUDE_SUBAGENT_NAME is absent, log "UNKNOWN_CHECK_PROBE"
    # so any reader knows this is an env var gap, not a real agent name.
    AGENT_NAME=$(safe_env "CLAUDE_SUBAGENT_NAME" "UNKNOWN_CHECK_PROBE")
    log_run "SubagentStart phase=$PHASE agent=$AGENT_NAME"

    cat >> "$METRICS_FILE" << EOF
- phase: $PHASE
  agent: $AGENT_NAME
  started: "$TIMESTAMP"
  status: in_progress
EOF
    ;;

  SubagentStop)
    PHASE=$(current_phase)
    AGENT_NAME=$(safe_env "CLAUDE_SUBAGENT_NAME" "UNKNOWN_CHECK_PROBE")
    EXIT_CODE=$(safe_env "CLAUDE_SUBAGENT_EXIT_CODE" "UNKNOWN_CHECK_PROBE")
    log_run "SubagentStop phase=$PHASE agent=$AGENT_NAME exit_code=$EXIT_CODE"

    cat >> "$METRICS_FILE" << EOF
  stopped: "$TIMESTAMP"
  exit_code: $EXIT_CODE
EOF
    ;;

  PostToolUse)
    TOOL_NAME=$(safe_env "CLAUDE_TOOL_NAME" "UNKNOWN_CHECK_PROBE")
    TOOL_EXIT=$(safe_env "CLAUDE_TOOL_EXIT_CODE" "UNKNOWN_CHECK_PROBE")
    log_tool "tool=$TOOL_NAME exit=$TOOL_EXIT"
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
    # $2 is "compact" when called from the post-compact SessionStart hook,
    # and absent when called directly (e.g. during testing). Only re-inject
    # state on a post-compact resume — a fresh session needs no injection.
    TRIGGER="${2:-fresh}"
    log_run "SessionStart trigger=$TRIGGER"

    if [ "$TRIGGER" = "compact" ]; then
      if [ -f "$PROJECT_ROOT/pipeline-state.yaml" ]; then
        echo ""
        echo "=== POST-COMPACT RESUME — pipeline-state.yaml ==="
        cat "$PROJECT_ROOT/pipeline-state.yaml"
        echo "=== END pipeline-state.yaml ==="
      else
        log_run "SessionStart compact — pipeline-state.yaml not found, nothing to re-inject"
      fi
    fi
    ;;

  *)
    log_run "UnknownEvent event=$EVENT"
    ;;

esac

exit 0
