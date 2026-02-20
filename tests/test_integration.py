from __future__ import annotations

import subprocess
import sys

from agentnotify.core.notifications import notify_run_completion, notify_watch_completion
from agentnotify.core.runner import ProcessRunner
from agentnotify.core.watcher import ProcessWatcher
from agentnotify.notify.base import NotificationLevel
from agentnotify.notify.null import NullNotifier


def test_integration_success_process_notifies() -> None:
    runner = ProcessRunner()
    notifier = NullNotifier()
    command = (
        "import time; print('progress 1', flush=True); "
        "time.sleep(0.2); print('done', flush=True)"
    )

    result = runner.run(
        [
            sys.executable,
            "-c",
            command,
        ],
        tool_name="integration",
        capture_output=True,
        tail_lines=5,
    )
    notify_run_completion(
        notifier,
        result,
        tool_name="integration",
        title_override=None,
        default_tool_name="Agent",
    )

    assert result.exit_code == 0
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0].level == NotificationLevel.SUCCESS


def test_integration_failure_process_notifies() -> None:
    runner = ProcessRunner()
    notifier = NullNotifier()

    result = runner.run(
        [
            sys.executable,
            "-c",
            "import sys, time; print('working', flush=True); time.sleep(0.2); sys.exit(2)",
        ],
        tool_name="integration",
        capture_output=True,
        tail_lines=5,
    )
    notify_run_completion(
        notifier,
        result,
        tool_name="integration",
        title_override=None,
        default_tool_name="Agent",
    )

    assert result.exit_code == 2
    assert len(notifier.notifications) == 1
    assert notifier.notifications[0].level == NotificationLevel.FAILURE


def test_integration_watch_mode_with_subprocess() -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time, sys; time.sleep(0.2); sys.exit(1)"]
    )
    watcher = ProcessWatcher(poll_interval=0.05, max_interval=0.1, backoff=1.0)
    result = watcher.wait_for_exit(process.pid)

    notifier = NullNotifier()
    notify_watch_completion(
        notifier,
        result,
        tool_name="integration-watch",
        title_override=None,
        default_tool_name="Agent",
    )

    assert result.pid == process.pid
    assert len(notifier.notifications) == 1
    if result.exit_code is not None:
        assert result.exit_code == 1
