"""Console notifier backend."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import Any, TextIO

from agentnotify.notify.base import NotificationLevel, Notifier


class ConsoleNotifier(Notifier):
    """Print notifications to stderr."""

    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stderr

    def notify(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        del metadata
        print(f"[agent-notify:{level.value}] {title}", file=self._stream)
        print(message, file=self._stream)
