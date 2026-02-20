# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- (none yet)

### Changed

- Removed `shell-init` process-exit notification mode from the CLI.
- Removed shell hook generation internals/tests and aligned project docs to task-level notifications only.

## [0.1.1] - 2026-02-20

### Changed

- Reworked README onboarding flow with clearer mode selection, per-tool setup recipes, and troubleshooting guidance.
- Clarified task-level vs shell-exit notification behavior to reduce setup confusion.
- Added `.release-venv/` to `.gitignore` to keep local release environments out of commits.

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
