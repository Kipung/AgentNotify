"""Config support via environment variables and optional TOML file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib

DEFAULT_CONFIG_PATH = Path.home() / ".agentnotify" / "config.toml"


@dataclass(slots=True)
class AppConfig:
    title_prefix: str = "Agent"
    channels: list[str] | None = None
    tail_lines: int = 20
    poll_interval: float = 1.0

    def __post_init__(self) -> None:
        if self.channels is None:
            self.channels = ["desktop"]


def _read_file_config(path: Path) -> dict[str, object]:
    if not path.exists() or not path.is_file():
        return {}

    with path.open("rb") as f:
        data = tomllib.load(f)

    if not isinstance(data, dict):
        return {}
    return data


def _parse_channels(raw: str | list[str] | None) -> list[str]:
    if raw is None:
        return ["desktop"]
    if isinstance(raw, list):
        channels = [part.strip().lower() for part in raw if part.strip()]
    else:
        channels = [part.strip().lower() for part in raw.split(",") if part.strip()]
    return channels or ["desktop"]


def load_config(path: Path | None = None) -> AppConfig:
    path = path or DEFAULT_CONFIG_PATH
    file_config = _read_file_config(path)

    title_prefix = str(file_config.get("title_prefix", "Agent"))
    channels = _parse_channels(file_config.get("channels"))
    tail_lines = int(file_config.get("tail_lines", 20))
    poll_interval = float(file_config.get("poll_interval", 1.0))

    if "AGENT_NOTIFY_TITLE_PREFIX" in os.environ:
        title_prefix = os.environ["AGENT_NOTIFY_TITLE_PREFIX"]
    if "AGENT_NOTIFY_CHANNELS" in os.environ:
        channels = _parse_channels(os.environ["AGENT_NOTIFY_CHANNELS"])
    if "AGENT_NOTIFY_TAIL_LINES" in os.environ:
        tail_lines = int(os.environ["AGENT_NOTIFY_TAIL_LINES"])
    if "AGENT_NOTIFY_POLL_INTERVAL" in os.environ:
        poll_interval = float(os.environ["AGENT_NOTIFY_POLL_INTERVAL"])

    return AppConfig(
        title_prefix=title_prefix,
        channels=channels,
        tail_lines=tail_lines,
        poll_interval=poll_interval,
    )
