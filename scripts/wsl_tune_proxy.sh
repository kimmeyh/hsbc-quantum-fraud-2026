#!/bin/bash
# F22 proxy tuning under WSL (A3 full-pair build). Args pass through to tune_proxy.py.
set -u
cd /mnt/d/Data/Harold/github/hsbc-quantum-fraud-2026 || { echo "FATAL: repo path not found"; exit 1; }
exec /root/eqc-venv/bin/python experiments/src/tune_proxy.py "$@"
