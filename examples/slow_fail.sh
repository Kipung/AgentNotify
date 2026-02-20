#!/usr/bin/env bash
set -euo pipefail

echo "[slow-fail] starting"
sleep 2
echo "[slow-fail] failing now"
exit 1
