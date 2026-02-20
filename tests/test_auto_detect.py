from __future__ import annotations

import platform
import subprocess

from agentnotify.cli import _infer_tool_name_from_command, _infer_tool_name_from_pid
from agentnotify.core.procinfo import get_process_name


def test_infer_tool_name_from_simple_command() -> None:
    assert _infer_tool_name_from_command(("codex", "run", "task")) == "codex"


def test_infer_tool_name_from_path_and_exe_suffix() -> None:
    assert _infer_tool_name_from_command(("/usr/local/bin/gemini.exe", "--help")) == "gemini"


def test_infer_tool_name_from_python_module() -> None:
    assert _infer_tool_name_from_command(("python3", "-m", "claude_code", "ask")) == "claude_code"


def test_get_process_name_posix(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(  # noqa: ANN002, ANN003
            args=args, returncode=0, stdout="codex\n", stderr=""
        ),
    )
    assert get_process_name(12345) == "codex"


def test_get_process_name_windows(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(  # noqa: ANN002, ANN003
            args=args, returncode=0, stdout="Code\n", stderr=""
        ),
    )
    assert get_process_name(12345) == "Code"


def test_infer_tool_name_from_pid_falls_back_to_pid(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("agentnotify.cli.get_process_name", lambda pid: None)
    assert _infer_tool_name_from_pid(777) == "pid-777"
