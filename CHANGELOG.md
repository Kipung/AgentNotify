# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- `gemini-hook` CLI command to consume Gemini hook payloads from `stdin` and notify on task-level events (defaults to `AfterAgent`).
- `claude-hook` CLI command to consume Claude hook payloads from `stdin` and notify on task-level events (defaults to `Stop`).
- `codex-hook` CLI command to consume Codex `notify` payloads from argument or `stdin` and notify on `agent-turn-complete`.
- `ollama-hook` CLI command to consume Ollama JSON/JSONL output and notify when `done=true`.
- README guidance and configuration example for task-level Gemini notifications via `~/.gemini/settings.json` hooks.
- README guidance and configuration examples for Codex `notify` and Claude hook setup.
- `gemini-hook --quiet-when-focused` option to suppress notifications while terminal is frontmost on macOS.
- `gemini-hook --chime` option (`none|bell|ping`) for optional sound alerts.
- Portable `examples/codex_notify_bridge.sh` that no longer depends on machine-specific paths.
- `docs/release_checklist.md` with Git/GitHub/tag/release steps.
- GitHub `Release Build` workflow (`.github/workflows/release.yml`) for tag-triggered lint/test/build checks.
- GitHub issue templates and pull request template for contributor-friendly triage/reviews.

### Changed

- Removed hardcoded absolute paths from README Codex setup examples.
- Expanded `.gitignore` with build artifacts, coverage files, logs, and temp debug outputs.

## [0.1.0] - 2026-02-20

### Added

- Initial release of `agent-notify`.
- `run` command to wrap long-running commands and notify on completion.
- `watch` command to monitor an existing PID.
- `test-notify` command for backend verification.
- Optional `tail` command for log pattern notification.
- macOS notifier using `osascript`.
- Windows notifier using PowerShell/BurntToast with `win10toast` fallback.
- Console and null notifier implementations.
- Unit and integration tests with mocked notifier coverage.
- GitHub Actions CI for macOS + Windows.
