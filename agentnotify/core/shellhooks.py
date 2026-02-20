"""Shell hook script generation for automatic notifications."""

from __future__ import annotations


def render_shell_init(
    *,
    shell: str,
    min_seconds: int,
    name: str,
    channel: str,
    notifier_bin: str,
    python_bin: str,
    project_root: str,
) -> str:
    """Render shell integration snippet for zsh or bash."""

    if shell == "zsh":
        return _render_zsh(
            min_seconds=min_seconds,
            name=name,
            channel=channel,
            notifier_bin=notifier_bin,
            python_bin=python_bin,
            project_root=project_root,
        )
    if shell == "bash":
        return _render_bash(
            min_seconds=min_seconds,
            name=name,
            channel=channel,
            notifier_bin=notifier_bin,
            python_bin=python_bin,
            project_root=project_root,
        )
    raise ValueError(f"Unsupported shell: {shell}")


def _escape_for_double_quotes(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace("$", "\\$")
    escaped = escaped.replace("`", "\\`")
    return escaped


def _render_zsh(
    *,
    min_seconds: int,
    name: str,
    channel: str,
    notifier_bin: str,
    python_bin: str,
    project_root: str,
) -> str:
    min_value = str(min_seconds)
    name_value = _escape_for_double_quotes(name)
    channel_value = _escape_for_double_quotes(channel)
    bin_value = _escape_for_double_quotes(notifier_bin)
    python_value = _escape_for_double_quotes(python_bin)
    project_root_value = _escape_for_double_quotes(project_root)

    return f"""# agent-notify shell integration (zsh)
typeset -g AGENT_NOTIFY_MIN_SECONDS="${{AGENT_NOTIFY_MIN_SECONDS:-{min_value}}}"
typeset -g AGENT_NOTIFY_NAME="${{AGENT_NOTIFY_NAME:-{name_value}}}"
typeset -g AGENT_NOTIFY_CHANNEL="${{AGENT_NOTIFY_CHANNEL:-{channel_value}}}"
typeset -g AGENT_NOTIFY_BIN="${{AGENT_NOTIFY_BIN:-{bin_value}}}"
typeset -g AGENT_NOTIFY_PYTHON="${{AGENT_NOTIFY_PYTHON:-{python_value}}}"
typeset -g AGENT_NOTIFY_PROJECT_ROOT="${{AGENT_NOTIFY_PROJECT_ROOT:-{project_root_value}}}"

typeset -g __agent_notify_started_at=""
typeset -g __agent_notify_command=""

_agent_notify_preexec() {{
  __agent_notify_started_at="$EPOCHSECONDS"
  __agent_notify_command="$1"
}}

_agent_notify_precmd() {{
  local exit_code="$?"
  if [[ -z "$__agent_notify_started_at" ]]; then
    return
  fi

  local end="$EPOCHSECONDS"
  local duration="$((end - __agent_notify_started_at))"
  local command="$__agent_notify_command"
  __agent_notify_started_at=""
  __agent_notify_command=""

  if [[ "$duration" -lt "$AGENT_NOTIFY_MIN_SECONDS" ]]; then
    return
  fi

  if [[ "$command" == *"agent-notify emit"* ]] || [[ "$command" == *"agentnotify.cli emit"* ]]; then
    return
  fi

  (
    if [[ -x "$AGENT_NOTIFY_BIN" ]]; then
      AGENT_NOTIFY_SHELL_HOOK=1 "$AGENT_NOTIFY_BIN" emit \\
        --name "$AGENT_NOTIFY_NAME" \\
        --command "$command" \\
        --duration-seconds "$duration" \\
        --exit-code "$exit_code" \\
        --channel "$AGENT_NOTIFY_CHANNEL" && exit 0
    fi
    AGENT_NOTIFY_SHELL_HOOK=1 \\
      PYTHONPATH="$AGENT_NOTIFY_PROJECT_ROOT${{PYTHONPATH:+:$PYTHONPATH}}" \\
      "$AGENT_NOTIFY_PYTHON" -m agentnotify.cli emit \\
      --name "$AGENT_NOTIFY_NAME" \\
      --command "$command" \\
      --duration-seconds "$duration" \\
      --exit-code "$exit_code" \\
      --channel "$AGENT_NOTIFY_CHANNEL"
  ) >/dev/null 2>&1 &!
}}

typeset -ga preexec_functions
typeset -ga precmd_functions
if (( ${{preexec_functions[(I)_agent_notify_preexec]}} == 0 )); then
  preexec_functions+=(_agent_notify_preexec)
fi
if (( ${{precmd_functions[(I)_agent_notify_precmd]}} == 0 )); then
  precmd_functions+=(_agent_notify_precmd)
fi
"""


def _render_bash(
    *,
    min_seconds: int,
    name: str,
    channel: str,
    notifier_bin: str,
    python_bin: str,
    project_root: str,
) -> str:
    min_value = str(min_seconds)
    name_value = _escape_for_double_quotes(name)
    channel_value = _escape_for_double_quotes(channel)
    bin_value = _escape_for_double_quotes(notifier_bin)
    python_value = _escape_for_double_quotes(python_bin)
    project_root_value = _escape_for_double_quotes(project_root)

    return f"""# agent-notify shell integration (bash)
AGENT_NOTIFY_MIN_SECONDS="${{AGENT_NOTIFY_MIN_SECONDS:-{min_value}}}"
AGENT_NOTIFY_NAME="${{AGENT_NOTIFY_NAME:-{name_value}}}"
AGENT_NOTIFY_CHANNEL="${{AGENT_NOTIFY_CHANNEL:-{channel_value}}}"
AGENT_NOTIFY_BIN="${{AGENT_NOTIFY_BIN:-{bin_value}}}"
AGENT_NOTIFY_PYTHON="${{AGENT_NOTIFY_PYTHON:-{python_value}}}"
AGENT_NOTIFY_PROJECT_ROOT="${{AGENT_NOTIFY_PROJECT_ROOT:-{project_root_value}}}"

__agent_notify_started_at=""
__agent_notify_command=""

__agent_notify_preexec() {{
  case "$BASH_COMMAND" in
    *__agent_notify_preexec*|*__agent_notify_precmd*|*"agent-notify emit"*|*"agentnotify.cli emit"*)
      return
      ;;
  esac
  __agent_notify_started_at="$(date +%s)"
  __agent_notify_command="$BASH_COMMAND"
}}

__agent_notify_precmd() {{
  local exit_code="$?"
  if [[ -z "$__agent_notify_started_at" ]]; then
    return
  fi

  local end="$(date +%s)"
  local duration="$((end - __agent_notify_started_at))"
  local command="$__agent_notify_command"
  __agent_notify_started_at=""
  __agent_notify_command=""

  if [[ "$duration" -lt "$AGENT_NOTIFY_MIN_SECONDS" ]]; then
    return
  fi
  if [[ "$command" == *"agent-notify emit"* ]] || [[ "$command" == *"agentnotify.cli emit"* ]]; then
    return
  fi

  (
    if [[ -x "$AGENT_NOTIFY_BIN" ]]; then
      AGENT_NOTIFY_SHELL_HOOK=1 "$AGENT_NOTIFY_BIN" emit \\
        --name "$AGENT_NOTIFY_NAME" \\
        --command "$command" \\
        --duration-seconds "$duration" \\
        --exit-code "$exit_code" \\
        --channel "$AGENT_NOTIFY_CHANNEL" && exit 0
    fi
    AGENT_NOTIFY_SHELL_HOOK=1 \\
      PYTHONPATH="$AGENT_NOTIFY_PROJECT_ROOT${{PYTHONPATH:+:$PYTHONPATH}}" \\
      "$AGENT_NOTIFY_PYTHON" -m agentnotify.cli emit \\
      --name "$AGENT_NOTIFY_NAME" \\
      --command "$command" \\
      --duration-seconds "$duration" \\
      --exit-code "$exit_code" \\
      --channel "$AGENT_NOTIFY_CHANNEL"
  ) >/dev/null 2>&1 &
}}

trap '__agent_notify_preexec' DEBUG
if [[ -n "${{PROMPT_COMMAND:-}}" ]]; then
  PROMPT_COMMAND="__agent_notify_precmd;${{PROMPT_COMMAND}}"
else
  PROMPT_COMMAND="__agent_notify_precmd"
fi
"""
