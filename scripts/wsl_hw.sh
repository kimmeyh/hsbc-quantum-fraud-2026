#!/bin/bash
# Metered hardware runner under WSL (Criterion H: team-lead approval required). Args pass through.
set -u
cd /mnt/d/Data/Harold/github/hsbc-quantum-fraud-2026 || { echo "FATAL: repo path not found"; exit 1; }
exec /root/eqc-venv/bin/python experiments/src/run_hardware.py "$@"
