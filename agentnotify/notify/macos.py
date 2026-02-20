"""macOS Notification Center notifier backend."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable, Mapping
from typing import Any

from agentnotify.notify.base import (
    NotificationError,
    NotificationLevel,
    Notifier,
    NotifierUnavailable,
)

RunCallable = Callable[..., subprocess.CompletedProcess[str]]


class MacOSNotifier(Notifier):
    """Send notifications through `osascript` on macOS."""

    def __init__(self, runner: RunCallable = subprocess.run) -> None:
        self._runner = runner

    def notify(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        del level, metadata
        if shutil.which("osascript") is None:
            raise NotifierUnavailable("osascript is not available on this system")

        script = (
            f'display notification "{_escape_applescript(message)}" '
            f'with title "{_escape_applescript(title)}"'
        )
        completed = self._runner(
            ["osascript", "-e", script],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise NotificationError(
                f"osascript failed with code {completed.returncode}: {completed.stderr.strip()}"
            )


def _escape_applescript(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"')
    return escaped
