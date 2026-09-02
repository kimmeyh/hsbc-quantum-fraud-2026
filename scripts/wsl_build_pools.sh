#!/bin/bash
# A3 full-pair pool builds (WSL; amendment A3). Idempotent: skips existing npz.
set -u
cd /mnt/d/Data/Harold/github/hsbc-quantum-fraud-2026
PY=/root/eqc-venv/bin/python
for s in 42 43 44 45 46 47 48 49 50 51; do
  out="experiments/results/pools/h_${s}_free_dct_full.npz"
  if [ -f "$out" ]; then echo "skip $out"; continue; fi
  echo "=== seed $s ==="
  "$PY" experiments/src/qubo_proxy.py build --seed "$s" --config free \
    --weak-type dct --pair-build full --out "$out" || echo "FAILED seed $s"
done
echo ALL_BUILDS_DONE
