"""Recover per-learner feature indices into pool metadata (F28 explainability)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "src"))
import qubo_proxy as qp

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
split, cols, Xtr, Xva, Xte, y = qp._prep(seed, 13)
clf = qp.build_pool(Xtr, y, 2, "dct", "full")
mp = qp.POOLS_DIR / f"h_{seed}_free_dct_full.meta.json"
m = json.loads(mp.read_text())
m["ind_list"] = [[int(j) for j in idx] for idx in clf.ind_list]
mp.write_text(json.dumps(m, indent=1))
print("ind_list added:", len(m["ind_list"]), "learners")
