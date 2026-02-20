# agent-notify

`agent-notify` is a cross-platform CLI utility that sends a notification when a long-running agentic command completes.

It is designed for Codex CLI/app, Claude Code, Gemini CLI, Antigravity, and any other process-based tooling.

## Features

- Wrap and run commands: `agent-notify run -- <cmd...>`
- Attach to existing processes: `agent-notify watch --pid <pid>`
- Notifications for success and failure
- Summary payload includes duration and exit code, with optional output tail lines
- macOS desktop notifications via Notification Center (`osascript`)
- Windows desktop notifications via PowerShell + BurntToast, with `win10toast` fallback
- Console fallback channel for unsupported environments

## Installation

Preferred:

```bash
pipx install agent-notify
```

Alternative:

```bash
pip install agent-notify
```

From source:

```bash
python -m pip install -e .
```

## Quickstart

Recommended: task-level hooks for interactive CLIs (no exit required).

### 1) Gemini CLI

Configure Gemini `AfterAgent` hook:

```json
{
  "hooksConfig": {
    "enabled": true
  },
  "hooks": {
    "AfterAgent": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "agent-notify gemini-hook --name gemini --channel both --quiet-when-focused --chime ping",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

### 2) Codex CLI

Codex has a built-in `notify` command hook that fires when an agent turn completes.
Use the provided bridge script:

```bash
chmod +x examples/codex_notify_bridge.sh
realpath examples/codex_notify_bridge.sh
```

Add this to `~/.codex/config.toml`:

```toml
notify = [
  "/absolute/path/to/examples/codex_notify_bridge.sh"
]
```

This wrapper handles Codex payload format differences and uses your installed `agent-notify`
binary when available. Optional debug logging is disabled by default and can be enabled with:

```bash
export AGENT_NOTIFY_DEBUG=1
```

Default debug log location:
`~/.agentnotify/logs/codex_notify.log`

### 3) Claude Code

Configure Claude hooks (project-local `.claude/settings.local.json` or user settings):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "agent-notify claude-hook --event Stop --name claude-code --channel both --quiet-when-focused --chime ping"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "agent-notify claude-hook --event SubagentStop --name claude-code --channel both --quiet-when-focused --chime ping"
          }
        ]
      }
    ]
  }
}
```

### 4) Ollama

- Pure `ollama run` does not expose a native task-finished hook in interactive mode.
- If using `ollama launch codex` or `ollama launch claude`, configure Codex/Claude hooks above and notifications still work.
- For non-interactive JSON output, you can pipe into:
  - `agent-notify ollama-hook --name ollama --channel both`

Legacy mode (process exit, not task-level):

```bash
eval "$(agent-notify shell-init --shell zsh --min-seconds 10 --channel both)"
```

Disable legacy shell-exit notifications:

```bash
sed -i '' '/agent-notify shell-init/d' ~/.zshrc
source ~/.zshrc
```

If you want only task-level notifications, do not enable `shell-init`.

## CLI Reference

### `agent-notify run -- <cmd...>`

- Wrapper exit code matches wrapped command exit code.

Options:

- `--name <tool>`: notification label
  - if omitted, `agent-notify` auto-detects from the wrapped command
- `--title <string>`: title override
- `--tail-lines <N>`: include last N output lines
- `--no-capture`: disable stdout/stderr tail capture
- `--channel desktop|console|both`: channel selection
- `--verbose`: verbose fallback/warning logs

Examples:

```bash
agent-notify run --name codex --tail-lines 20 -- codex run "build docs"
agent-notify run --channel both -- python -c "import time; time.sleep(3)"
```

### `agent-notify watch --pid <pid>`

Options:

- `--name`, `--title`, `--channel`, `--verbose`
  - if `--name` is omitted, `agent-notify` tries to detect process name from PID
- `--poll-interval <seconds>`

Example:

```bash
python -c "import time; time.sleep(5)" &
agent-notify watch --pid $! --name background-job
```

### `agent-notify tail --file <path> --pattern <text>`

Optional log watcher mode that notifies when a pattern appears.

### `agent-notify test-notify`

Sends a sample notification through the selected channel.

### `agent-notify emit` (integration/internal)

Sends a completion notification from external hooks with explicit command metadata.

### `agent-notify gemini-hook`

Reads a Gemini hook JSON payload from `stdin` and notifies for matching events.

Default behavior:

- Event trigger: `AfterAgent`
- Tool label: `gemini`

Useful flags:

- `--event <name>`: trigger on a different hook event
- `--name <tool>`: notification label
- `--channel desktop|console|both`
- `--quiet-when-focused`: suppress notification while terminal is in focus (macOS)
- `--chime none|bell|ping`: optional sound when notifying

### `agent-notify claude-hook`

Reads a Claude hook JSON payload from `stdin` and notifies for matching events.

Default behavior:

- Event trigger: `Stop`
- Tool label: `claude-code`

Useful flags:

- `--event <name>`: trigger on a different hook event (for example `SubagentStop`)
- `--name <tool>`: notification label
- `--channel desktop|console|both`
- `--quiet-when-focused`: suppress notification while terminal is in focus (macOS)
- `--chime none|bell|ping`: optional sound when notifying

### `agent-notify codex-hook [payload]`

Reads a Codex `notify` JSON payload (argument or `stdin`) and notifies for matching events.

Default behavior:

- Event trigger: `agent-turn-complete`
- Tool label: `codex`

Useful flags:

- `--event <name>`: trigger on a different Codex event type
- `--name <tool>`: notification label
- `--channel desktop|console|both`
- `--quiet-when-focused`: suppress notification while terminal is in focus (macOS)
- `--chime none|bell|ping`: optional sound when notifying

### `agent-notify ollama-hook`

Reads Ollama JSON/JSONL output from `stdin` (use `ollama run --format json`) and notifies on `done=true`.

### `agent-notify shell-init`

Prints a shell hook script for `zsh`/`bash`. This mode notifies on process exit, not on task-level agent events.

## Notification Content

Default title:

- Success: `[<tool>] Done`
- Failure: `[<tool>] Failed`
- If no tool is provided, defaults to `[Agent] ...` (configurable).

Body includes:

- Duration (human readable)
- Exit code (or `unknown` when unavailable)
- Optional tail output lines

Long bodies are truncated safely.

## Configuration

Environment variables:

- `AGENT_NOTIFY_TITLE_PREFIX="Agent"`
- `AGENT_NOTIFY_CHANNELS="desktop,console"`
- `AGENT_NOTIFY_TAIL_LINES=20`
- `AGENT_NOTIFY_POLL_INTERVAL=1.0`

Optional TOML file:

`~/.agentnotify/config.toml`

```toml
title_prefix = "Agent"
channels = ["desktop"]
tail_lines = 20
poll_interval = 1.0
```

Environment variables override config file values.

## Platform Notes

### macOS

Uses:

```bash
osascript -e 'display notification "..." with title "..."'
```

If unavailable, `agent-notify` falls back to console output.

### Windows

Primary backend:

- PowerShell + BurntToast (`New-BurntToastNotification`)

Install BurntToast:

```powershell
Install-Module BurntToast -Scope CurrentUser
```

Fallback backend:

- Python `win10toast` (optional):

```bash
pip install "agent-notify[windows]"
```

## Examples

Demo scripts:

- `examples/slow_success.sh`
- `examples/slow_fail.sh`

Run:

```bash
agent-notify run --name demo -- ./examples/slow_success.sh
agent-notify run --name demo -- ./examples/slow_fail.sh
```

## Development

Install dev tools and run checks:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m build
twine check dist/*
```

## GitHub Release

Before first public release:

1. Update repository links in `pyproject.toml` (`[project.urls]`).
2. Confirm package metadata and version (`agentnotify/__init__.py`, `pyproject.toml`, `CHANGELOG.md`).
3. Run local checks (`ruff check .` and `pytest -q`).
4. Follow the release checklist in `docs/release_checklist.md`.

## Project Management

- Project charter: `docs/project_charter.md`
- Scrum working agreement: `docs/scrum_working_agreement.md`
- Assumptions log: `docs/assumptions.md`
- Suggested commit sequencing: `docs/commit_plan.md`
- Release checklist: `docs/release_checklist.md`
- Security policy: `SECURITY.md`

## Roadmap

- Linux desktop backend plugin
- Webhook/Slack channel
- Cooldown/debounce controls
- System tray integration

## License

MIT (`LICENSE`)
