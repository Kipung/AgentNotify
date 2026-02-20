from __future__ import annotations

from agentnotify.core.shellhooks import render_shell_init


def test_render_zsh_shell_init_contains_expected_hooks() -> None:
    script = render_shell_init(
        shell="zsh",
        min_seconds=15,
        name="Agent",
        channel="both",
        notifier_bin="/tmp/agent-notify",
        python_bin="/tmp/python3",
        project_root="/tmp/project",
    )
    assert "agent-notify shell integration (zsh)" in script
    assert 'AGENT_NOTIFY_MIN_SECONDS="${AGENT_NOTIFY_MIN_SECONDS:-15}"' in script
    assert 'AGENT_NOTIFY_CHANNEL="${AGENT_NOTIFY_CHANNEL:-both}"' in script
    assert 'AGENT_NOTIFY_BIN="${AGENT_NOTIFY_BIN:-/tmp/agent-notify}"' in script
    assert 'AGENT_NOTIFY_PROJECT_ROOT="${AGENT_NOTIFY_PROJECT_ROOT:-/tmp/project}"' in script
    assert "_agent_notify_preexec" in script
    assert "_agent_notify_precmd" in script
    assert '"$AGENT_NOTIFY_BIN" emit' in script
    assert '&!' in script


def test_render_bash_shell_init_contains_expected_hooks() -> None:
    script = render_shell_init(
        shell="bash",
        min_seconds=8,
        name="Shell",
        channel="desktop",
        notifier_bin="/tmp/agent-notify",
        python_bin="/tmp/python3",
        project_root="/tmp/project",
    )
    assert "agent-notify shell integration (bash)" in script
    assert 'AGENT_NOTIFY_MIN_SECONDS="${AGENT_NOTIFY_MIN_SECONDS:-8}"' in script
    assert 'AGENT_NOTIFY_NAME="${AGENT_NOTIFY_NAME:-Shell}"' in script
    assert 'AGENT_NOTIFY_PYTHON="${AGENT_NOTIFY_PYTHON:-/tmp/python3}"' in script
    assert 'AGENT_NOTIFY_PROJECT_ROOT="${AGENT_NOTIFY_PROJECT_ROOT:-/tmp/project}"' in script
    assert "trap '__agent_notify_preexec' DEBUG" in script
    assert 'PROMPT_COMMAND="__agent_notify_precmd"' in script


def test_render_shell_init_rejects_unknown_shell() -> None:
    try:
        render_shell_init(
            shell="fish",
            min_seconds=5,
            name="Agent",
            channel="desktop",
            notifier_bin="/tmp/agent-notify",
            python_bin="/tmp/python3",
            project_root="/tmp/project",
        )
    except ValueError as exc:
        assert "Unsupported shell" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
