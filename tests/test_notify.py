from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from agentnotify.core.notifications import notify_run_completion, notify_watch_completion
from agentnotify.core.result import RunResult, WatchResult
from agentnotify.notify.base import (
    CompositeNotifier,
    NotificationLevel,
    Notifier,
    NotifierUnavailable,
)
from agentnotify.notify.macos import MacOSNotifier
from agentnotify.notify.null import NullNotifier
from agentnotify.notify.windows import WindowsNotifier


def test_notifier_called_with_expected_fields() -> None:
    notifier = NullNotifier()
    result = RunResult(
        command=["codex", "run"],
        exit_code=0,
        duration_seconds=12.5,
        output_tail=["step 1", "step 2"],
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        tool_name="codex",
    )

    title, body, level = notify_run_completion(
        notifier,
        result,
        tool_name="codex",
        title_override=None,
        default_tool_name="Agent",
    )

    assert title == "[codex] Done"
    assert "Duration:" in body
    assert "Exit code: 0" in body
    assert level == NotificationLevel.SUCCESS

    assert len(notifier.notifications) == 1
    sent = notifier.notifications[0]
    assert sent.title == "[codex] Done"
    assert sent.level == NotificationLevel.SUCCESS
    assert sent.metadata is not None
    assert sent.metadata["exit_code"] == 0


def test_watch_notification_with_unknown_exit_is_not_marked_failed() -> None:
    notifier = NullNotifier()
    result = WatchResult(
        pid=12345,
        duration_seconds=4.2,
        exit_code=None,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        already_exited=False,
    )

    title, _, level = notify_watch_completion(
        notifier,
        result,
        tool_name="watcher",
        title_override=None,
        default_tool_name="Agent",
    )

    assert title == "[watcher] Done"
    assert level == NotificationLevel.INFO


def test_macos_notifier_raises_when_osascript_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agentnotify.notify.macos.shutil.which", lambda _: None)
    notifier = MacOSNotifier()

    with pytest.raises(NotifierUnavailable):
        notifier.notify("Title", "Message")


def test_windows_notifier_uses_powershell_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agentnotify.notify.windows.platform.system", lambda: "Windows")

    def fake_runner(*args, **kwargs):  # noqa: ANN002, ANN003
        del args, kwargs
        return subprocess.CompletedProcess(args=["powershell"], returncode=0, stdout="", stderr="")

    notifier = WindowsNotifier(runner=fake_runner)
    notifier.notify("Title", "Message")


def test_windows_notifier_falls_back_to_win10toast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agentnotify.notify.windows.platform.system", lambda: "Windows")

    def fake_runner(*args, **kwargs):  # noqa: ANN002, ANN003
        del args, kwargs
        return subprocess.CompletedProcess(args=["powershell"], returncode=2, stdout="", stderr="")

    class _ToastModule:
        class ToastNotifier:  # noqa: D106
            def show_toast(self, title, message, duration=5, threaded=False):  # noqa: ANN001, ANN201
                del title, message, duration, threaded
                return True

    monkeypatch.setattr(
        "agentnotify.notify.windows.importlib.import_module",
        lambda name: _ToastModule() if name == "win10toast" else None,
    )

    notifier = WindowsNotifier(runner=fake_runner)
    notifier.notify("Title", "Message")


def test_windows_notifier_raises_when_no_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agentnotify.notify.windows.platform.system", lambda: "Windows")

    def fake_runner(*args, **kwargs):  # noqa: ANN002, ANN003
        del args, kwargs
        return subprocess.CompletedProcess(args=["powershell"], returncode=2, stdout="", stderr="")

    def fake_import(name: str) -> SimpleNamespace:
        del name
        raise ImportError("not installed")

    monkeypatch.setattr("agentnotify.notify.windows.importlib.import_module", fake_import)

    notifier = WindowsNotifier(runner=fake_runner)
    with pytest.raises(NotifierUnavailable):
        notifier.notify("Title", "Message")


def test_composite_notifier_delivers_when_one_backend_fails() -> None:
    class _FailingNotifier(Notifier):
        def notify(self, title, message, level=NotificationLevel.INFO, metadata=None):  # noqa: ANN001, ANN201
            del title, message, level, metadata
            raise RuntimeError("desktop unavailable")

    capture = NullNotifier()
    composite = CompositeNotifier([_FailingNotifier(), capture])
    composite.notify("Title", "Message")

    assert len(capture.notifications) == 1
    assert capture.notifications[0].title == "Title"
