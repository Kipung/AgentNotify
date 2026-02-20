#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${AGENT_NOTIFY_PROJECT_ROOT:-$(cd -- "$SCRIPT_DIR/.." && pwd)}"
AGENT_NOTIFY_BIN="${AGENT_NOTIFY_BIN:-$(command -v agent-notify || true)}"

if [[ -z "${AGENT_NOTIFY_PYTHON:-}" ]]; then
  if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    AGENT_NOTIFY_PYTHON="$PROJECT_ROOT/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    AGENT_NOTIFY_PYTHON="$(command -v python3)"
  else
    AGENT_NOTIFY_PYTHON="$(command -v python)"
  fi
fi

if [[ "${AGENT_NOTIFY_DEBUG:-0}" == "1" ]]; then
  LOG_DIR="${AGENT_NOTIFY_CODEX_LOG_DIR:-$HOME/.agentnotify/logs}"
  LOG_FILE="${AGENT_NOTIFY_CODEX_LOG:-$LOG_DIR/codex_notify.log}"
  if mkdir -p "$LOG_DIR" >/dev/null 2>&1; then
    {
      printf -- '--- %s ---\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf 'argc=%s\n' "$#"
      index=1
      for arg in "$@"; do
        printf 'arg%d=%s\n' "$index" "$arg"
        index=$((index + 1))
      done
    } >>"$LOG_FILE" 2>/dev/null || true
  fi
fi

if [[ -n "$AGENT_NOTIFY_BIN" ]]; then
  exec "$AGENT_NOTIFY_BIN" codex-hook \
    --name codex \
    --channel both \
    --quiet-when-focused \
    --chime ping \
    "$@"
fi

exec env PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
  "$AGENT_NOTIFY_PYTHON" -m agentnotify.cli codex-hook \
  --name codex \
  --channel both \
  --quiet-when-focused \
  --chime ping \
  "$@"
