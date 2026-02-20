# agent-notify

`agent-notify` sends notifications when long-running CLI/agent tasks finish.

It supports two usage styles:

1. Wrap a command (`agent-notify run -- ...`)
2. Receive task-level events from interactive agents (Codex, Claude Code, Gemini, Ollama pipelines)

## Why People Use This

- You can keep coding in one window and get notified when a background task completes.
- Notifications include success/failure, duration, and exit code.
- Works on macOS and Windows (with console fallback when desktop notifications are unavailable).

## Install

Recommended:

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

Confirm install:

```bash
agent-notify --help
agent-notify test-notify --channel console
```

## 2-Minute Quickstart

Run any long command through the wrapper:

```bash
agent-notify run -- python3 -c "import time; time.sleep(8)"
```

If the command fails, the notification title changes to `Failed`.

## Choose Your Mode

### Mode A: Task-Level Notifications (Recommended for interactive CLIs)

This notifies when an agent turn/task completes inside Codex/Claude/Gemini flows.
You do not need to exit the CLI session.

### Mode B: Shell Exit Notifications (`shell-init`)

This notifies when shell commands end. For interactive agents, that usually means on CLI exit.
Use this only if you want process-exit behavior.

## Interactive Tool Setup

### Codex CLI

Codex provides a `notify` hook. Use the included bridge:

```bash
chmod +x examples/codex_notify_bridge.sh
BRIDGE_PATH="$(realpath examples/codex_notify_bridge.sh)"
echo "$BRIDGE_PATH"
```

Add to `~/.codex/config.toml`:

```toml
notify = [
  "/absolute/path/to/examples/codex_notify_bridge.sh"
]
```

Optional debug logs:

```bash
export AGENT_NOTIFY_DEBUG=1
```

Log location:
`~/.agentnotify/logs/codex_notify.log`

### Claude Code

Configure hooks in `.claude/settings.local.json` (or user settings):

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

### Gemini CLI

Configure `AfterAgent` hook:

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

### Ollama

- Pure interactive `ollama run` currently has no native per-turn completion hook.
- If you use `ollama launch codex` or `ollama launch claude`, configure Codex/Claude hooks above.
- For non-interactive JSON output (`--format json`), pipe into `agent-notify ollama-hook`.

Example:

```bash
ollama run llama3 --format json | agent-notify ollama-hook --name ollama --channel both
```

## Core Commands

`agent-notify run -- <cmd...>`
- Run and notify on completion.
- Wrapper exits with the same exit code as the wrapped command.

`agent-notify watch --pid <pid>`
- Watch an existing process ID until exit.

`agent-notify test-notify`
- Send a sample notification.

`agent-notify tail --file <path> --pattern <text>`
- Notify when a log pattern appears.

`agent-notify shell-init`
- Generate shell hook script for process-exit notifications.

Hook bridge commands used by integrations:
- `agent-notify gemini-hook`
- `agent-notify claude-hook`
- `agent-notify codex-hook`
- `agent-notify ollama-hook`

## Common Customizations

Suppress notifications while terminal is focused (macOS):

```bash
agent-notify gemini-hook --quiet-when-focused
```

Add sound:

```bash
agent-notify claude-hook --chime ping
```

Force console output:

```bash
agent-notify run --channel console -- your-command
```

## Configuration

Environment variables:

- `AGENT_NOTIFY_TITLE_PREFIX="Agent"`
- `AGENT_NOTIFY_CHANNELS="desktop,console"`
- `AGENT_NOTIFY_TAIL_LINES=20`
- `AGENT_NOTIFY_POLL_INTERVAL=1.0`

Optional TOML config at `~/.agentnotify/config.toml`:

```toml
title_prefix = "Agent"
channels = ["desktop"]
tail_lines = 20
poll_interval = 1.0
```

Environment variables override file values.

## Troubleshooting

### I only get notifications when I exit the CLI

You are likely using `shell-init` mode. That is process-exit based.

Use task-level hooks (`codex-hook`, `claude-hook`, `gemini-hook`) instead and remove `shell-init` lines from your shell startup file.

### Desktop notifications do not appear

1. Test fallback path:
   - `agent-notify test-notify --channel console`
2. Verify platform backend:
   - macOS uses `osascript`
   - Windows uses PowerShell/BurntToast (with `win10toast` fallback)

### Codex notifications not firing

1. Confirm `notify` is configured in `~/.codex/config.toml`.
2. Confirm bridge script is executable: `chmod +x examples/codex_notify_bridge.sh`.
3. Enable bridge debug logs with `AGENT_NOTIFY_DEBUG=1` and inspect `~/.agentnotify/logs/codex_notify.log`.

## Platform Notes

macOS:
- Desktop notifications via Notification Center (`osascript`).

Windows:
- Primary backend: PowerShell + BurntToast.
- Optional fallback dependency: `pip install "agent-notify[windows]"`.

## For Maintainers

Development checks:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m build
twine check dist/*
```

Release checklist:
- `docs/release_checklist.md`

Project/process docs:
- `docs/project_charter.md`
- `docs/scrum_working_agreement.md`
- `docs/assumptions.md`
- `docs/commit_plan.md`
- `SECURITY.md`

## License

MIT (`LICENSE`)
