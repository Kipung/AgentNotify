from __future__ import annotations

import os
import platform
import subprocess
import sys

import pytest

from agentnotify.core.watcher import ProcessWatcher, pid_exists


def _missing_pid() -> int:
    candidate = os.getpid() + 100_000
    while pid_exists(candidate):
        candidate += 1
    return candidate


def test_watcher_handles_missing_pid_immediately() -> None:
    watcher = ProcessWatcher(poll_interval=0.05, max_interval=0.1, backoff=1.0)
    result = watcher.wait_for_exit(_missing_pid())

    assert result.already_exited is True
    assert result.exit_code is None


def test_watcher_waits_for_running_process() -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "import time, sys; time.sleep(0.3); sys.exit(0)"]
    )

    watcher = ProcessWatcher(poll_interval=0.05, max_interval=0.1, backoff=1.0)
    result = watcher.wait_for_exit(process.pid)

    assert result.pid == process.pid
    assert result.already_exited is False
    assert result.duration_seconds >= 0.2
    if result.exit_code is not None:
        assert result.exit_code == 0


def test_pid_exists_windows_true_without_os_kill(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    def fail_kill(pid: int, sig: int) -> None:
        del pid, sig
        raise AssertionError("os.kill should not be used on Windows pid checks")

    monkeypatch.setattr(os, "kill", fail_kill)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(  # noqa: ANN002, ANN003
            args=args,
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    assert pid_exists(4242) is True


def test_pid_exists_windows_false_without_os_kill(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(platform, "system", lambda: "Windows")

    def fail_kill(pid: int, sig: int) -> None:
        del pid, sig
        raise AssertionError("os.kill should not be used on Windows pid checks")

    monkeypatch.setattr(os, "kill", fail_kill)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(  # noqa: ANN002, ANN003
            args=args,
            returncode=1,
            stdout="",
            stderr="",
        ),
    )

    assert pid_exists(4242) is False
