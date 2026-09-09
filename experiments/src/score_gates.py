"""Gate scoring and campaign aggregation (Sprint 3 B4/B6; amendment A4).

Reads results.json + tuned_params.json and produces experiments/results/
gate_report.md with: G0 scored as committed, per-arm across-seed summaries,
the Tuning Budget Equivalence table, paired-delta SD + MDE refinement input,
and the A3 sequential-vs-full-pair comparison with its preregistered selection.

Read-only over the evidence store; safe to run at any time (reports on
whatever rows exist and says what is missing).

Usage: python experiments/src/score_gates.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
G0_FLOOR = 0.85          # prereg 3: tuned-XGB mean AP >= 0.85 (0.85-0.88 honest band)
G0_LEAK_FLAG = 0.95      # >0.95 = leakage flag
MDE = 0.0268             # amendment A5 (measured paired-delta MDE); single source
N_SEEDS = 10


def _fit_table_widths(lines: list[str]) -> list[str]:
    """Rewrite every pipe-table separator to reflect real column content.

    pandoc sizes a pipe-table column by the DASH COUNT in its separator row.
    Every table here was written `|---|---|`, which gives each column an equal
    share -- so the 37-character Cell column got the same width as the
    5-character Seeds column and its text ran into the neighbour. The rendered
    PDF showed "catboost/matched1013" and
    "cvqboost_hw/hw_b1_dct/strat0.7671ified/full": collisions, not truncation.

    Widths are derived from the widest cell actually present, so they stay
    correct as rows come and go. A minimum of 3 keeps the separator valid, and
    the whole row is scaled to a sane total so one very long column cannot
    squeeze the rest to nothing.
    """
    out = list(lines)
    i = 0
    while i < len(out):
        sep_i = i + 1
        if (out[i].startswith("| ") and sep_i < len(out)
                and out[sep_i].startswith("|")
                and set(out[sep_i].replace("|", "").strip()) <= set("-: ")):
            header = [c.strip() for c in out[i].strip("|").split("|")]
            rows = []
            j = sep_i + 1
            while j < len(out) and out[j].startswith("|"):
                rows.append([c.strip() for c in out[j].strip("|").split("|")])
                j += 1
            widths = []
            for k, h in enumerate(header):
                cells = [len(r[k]) for r in rows if k < len(r)]
                # +2 of padding per column: pandoc sizes to the RATIO, and a
                # column sized to exactly its longest cell still renders that
                # cell flush against its neighbour.
                widths.append(max([len(h)] + cells) + 6)
            # Scale to ~110 columns total: wide enough that pandoc's relative
            # widths are meaningful, small enough to stay on the page.
            # Cap any single column at 40% of the row. Without this the Cell
            # column (44 chars vs a 4-char Rows column) takes so large a share
            # that pandoc leaves its neighbour almost no width, and the two
            # render flush against each other. Capping forces the long names to
            # WRAP inside their cell, which is readable, instead of colliding
            # with the next column, which is not.
            total = sum(widths) or 1
            # Floor of 8, not 3. A column scaled to 4 characters sits flush
            # against its neighbour no matter how much padding the wide column
            # got: "stratified/full1" was Cell running into a Rows value of 1,
            # because Rows had scaled down to almost nothing beside a 44-char
            # Cell. The floor costs the wide column a little and fixes it.
            scaled = [max(8, round(w * 130 / total)) for w in widths]
            out[sep_i] = "|" + "|".join("-" * w for w in scaled) + "|"
            i = j
        else:
            i += 1
    return out


def is_metered_arm(row) -> bool:
    """True for a row belonging to an arm that consumes device seconds.

    Exported so tests assert against the SAME predicate the report uses. The
    first version of test_gate_report_totals.py restated the rule as "any row
    with truthy metered_seconds", which agreed with this only by coincidence of
    today's data: a future metered arm not named cvqboost_hw* would be counted
    by the test and excluded by the report, and the failure would misdirect to
    "the arm filter has narrowed again".
    """
    return str(row.get("arm", "")).startswith("cvqboost_hw")


def main() -> int:
    store = json.loads((RESULTS_DIR / "results.json").read_text())
    rows = store["rows"]
    tuned = json.loads((RESULTS_DIR / "tuned_params.json").read_text()) \
        if (RESULTS_DIR / "tuned_params.json").exists() else {}

    by_cell = defaultdict(list)
    quarantined = 0
    for r in rows:
        if r["arm"] == "cvqboost_proxy":
            # Team-lead validation 2026-09-02: lg pools are QUARANTINED from all
            # tables until fixed -- degenerate scoring (99.8% identical scores;
            # alert budget flags everything). Root cause: frozen lambda=2*n_train
            # (SPECTRA-calibrated) + unweighted weak learners on 0.17% positives.
            # Fix path: the preregistered section-6 proxy tuning (F22).
            if r["pool_variant"] == "lg" and r.get("config") == "free":   # starting-config lg only; tuned lg re-enters if healthy
                quarantined += 1
                continue
            key = (r["arm"], r["config"], r["pool_variant"], r["pair_build"])
        elif str(r["arm"]).startswith("cvqboost_hw"):
            # startswith, matching the metered-arm selection below. This branch
            # used to test == "cvqboost_hw", so a cvqboost_hw_mixed row fell to
            # the else and was keyed WITHOUT the status guard. run_hardware_f32
            # writes failed fits as {"status": "failed", "metrics": None}, and
            # the across-seed summary then dereferences metrics["auprc"] on
            # None. Latent only because all 10 mixed rows are currently ok; the
            # first failed mixed fit would take down the report generator.
            if r.get("status") != "ok":
                continue                      # failed cells summarized separately
            key = (r["arm"], r["config"], r["protocol"], r["pair_build"])
        else:
            key = (r["arm"], r["feature_set"])
        by_cell[key].append(r)

    n_hw = sum(1 for r in rows if r.get("evidence_tag") == "HW")
    n_sim = sum(1 for r in rows if r.get("evidence_tag") == "SIM")
    lines = ["# Gate Report (generated by score_gates.py)", "",
             f"Rows: {len(rows)} ({n_sim} [SIM], {n_hw} [HW]). Every number below traces to "
             "results.json; each cell carries the evidence tag of the rows it summarizes "
             "(cvqboost_hw and cvqboost_hw_mixed cells are [HW], all others [SIM]).", ""]
    if quarantined:
        lines += [f"NOTE: {quarantined} lg-pool proxy rows are QUARANTINED from all tables "
                  "(team-lead validation 2026-09-02: degenerate scoring -- ~99.8% identical "
                  "scores, alert budget unusable). Rows remain in results.json; they return "
                  "to tables after the F22 proxy-tuning fix.", "",
                  "CAVEAT on dct proxy cells: scores take ~120 distinct values with ~96% of "
                  "transactions at the mode (near-uniform weights under the frozen "
                  "lambda=2*n_train starting config). AUPRC/AUC handle the ties correctly "
                  "(step-wise AP; tie_fraction recorded per row), but alert-budget precision "
                  "and calibration numbers are weaker evidence until F22 tunes lambda and "
                  "pool composition per prereg section 6.", ""]

    # ---- per-cell summaries ----
    lines += ["## Across-seed summaries (test AUPRC; prevalence beside it)", "",
              "| Cell | Seeds | Mean AP | Seed SD | t-95% CI | Mean AUC | Prevalence |",
              "|---|---|---|---|---|---|---|"]
    cell_aps = {}
    for key in sorted(by_cell, key=str):
        cell = by_cell[key]
        aps = [r["metrics"]["auprc"] for r in cell]
        aucs = [r["metrics"]["auc_roc"] for r in cell]
        prev = cell[0]["metrics"]["prevalence"]
        cell_aps[key] = {r["seed"]: r["metrics"]["auprc"] for r in cell}
        ti = metrics.seed_mean_t_interval(aps) if len(aps) >= 2 else None
        ci = f"[{ti['ci95'][0]:.4f}, {ti['ci95'][1]:.4f}]" if ti else "n/a"
        lines.append(
            f"| {'/'.join(str(k) for k in key)} | {len(aps)} | {np.mean(aps):.4f} "
            f"| {np.std(aps, ddof=1):.4f} | {ci} | {np.mean(aucs):.4f} | {prev:.5f} |"
            if len(aps) >= 2 else
            f"| {'/'.join(str(k) for k in key)} | {len(aps)} | {np.mean(aps):.4f} "
            f"| n/a | n/a | {np.mean(aucs):.4f} | {prev:.5f} |")
    lines.append("")

    # ---- score health (A6) ----
    lines += ["## Score health (amendment A6; WARN = degenerate score distribution)", "",
              "| Cell | Rows | WARN rows | Median mode share | Median n_distinct |", "|---|---|---|---|---|"]
    for key in sorted(by_cell, key=str):
        cell = by_cell[key]
        hs = [r["metrics"].get("score_health") for r in cell]
        hs = [h for h in hs if h]
        if not hs:
            lines.append(f"| {'/'.join(str(k) for k in key)} | {len(cell)} | n/a (pre-A6 rows) | n/a | n/a |")
            continue
        lines.append(f"| {'/'.join(str(k) for k in key)} | {len(cell)} | {sum(h['warn'] for h in hs)} "
                     f"| {np.median([h['mode_share'] for h in hs]):.3f} | {int(np.median([h['n_distinct'] for h in hs]))} |")
    lines.append("")

    # ---- G0 ----
    xgb_full = cell_aps.get(("xgboost", "full"), {})
    lines += ["## G0 (tuned-XGB full features, mean test AP >= 0.85)", ""]
    if len(xgb_full) >= N_SEEDS:
        mean_ap = float(np.mean(list(xgb_full.values())))
        verdict = "PASS" if mean_ap >= G0_FLOOR else "FAIL"
        leak = " LEAKAGE FLAG (>0.95): investigate before any claim" if mean_ap > G0_LEAK_FLAG else ""
        lines.append(f"Mean AP = {mean_ap:.4f} over {len(xgb_full)} seeds -> **{verdict}**{leak}")
    else:
        lines.append(f"UNSCOREABLE YET: {len(xgb_full)}/{N_SEEDS} xgboost/full seeds present.")
    lines.append("")

    # ---- paired delta: proxy CVQBoost (free/dct/sequential) vs best GBDT matched ----
    lines += ["## Paired per-seed deltas (H1b machinery check; matched features)", ""]
    gbdt_cells = {a: cell_aps.get((a, "matched13"), {})
                  for a in ("xgboost", "lightgbm", "catboost")}
    complete = {a: c for a, c in gbdt_cells.items() if len(c) >= N_SEEDS}
    # Proxy cell = the config SELECTED on validation AP (A3 rule applied to
    # configs): highest mean val_auprc across seeds among full-pair proxy cells.
    val_means = {k: np.mean([r["val_auprc"] for r in by_cell[k]])
                 for k in by_cell if k[0] == "cvqboost_proxy" and k[3] == "full"
                 and len(by_cell[k]) >= N_SEEDS}
    proxy_key = max(val_means, key=val_means.get) if val_means else ("cvqboost_proxy", "free", "dct", "sequential")
    proxy = cell_aps.get(proxy_key, {})
    lines.append(f"Proxy cell used: {'/'.join(str(x) for x in proxy_key)}")
    if complete and len(proxy) >= N_SEEDS:
        best_arm = max(complete, key=lambda a: np.mean(list(complete[a].values())))
        seeds = sorted(set(proxy) & set(complete[best_arm]))
        deltas = [proxy[s] - complete[best_arm][s] for s in seeds]
        ti = metrics.seed_mean_t_interval(deltas)
        sd = float(np.std(deltas, ddof=1))
        lines += [f"Best matched GBDT: {best_arm}. Delta = proxy_CVQBoost - {best_arm}, "
                  f"{len(seeds)} seeds.",
                  f"Mean delta {ti['mean']:+.4f}, seed SD {sd:.4f}, "
                  f"95% CI [{ti['ci95'][0]:+.4f}, {ti['ci95'][1]:+.4f}].",
                  f"MDE(10 seeds) recomputed from this SD: {metrics.mde(sd, N_SEEDS):.4f} "
                  f"(adjudication uses the amendment-A5 value {MDE}; any change is Class-1)."]
    else:
        lines.append("UNSCOREABLE YET: needs 10-seed matched GBDT cells and 10 proxy seeds.")
    lines.append("")

    # ---- hardware rows + G0b (Spearman over the 5 ranked configs) ----
    # EVERY metered arm, not just cvqboost_hw. This filter used to read
    # `== "cvqboost_hw"`, which silently dropped the 10 cvqboost_hw_mixed fits
    # (43.0 s) from the campaign total, so the generated report said 27 fits /
    # 120.0 s while results.json held 37 / 163.0 s. The appendix quoted the true
    # figure and the proposal quoted the report's, which is how the two came to
    # disagree in the submission. Found by the Fable 5.1 review, 2026-09-09.
    #
    # This is the file CLAUDE.md designates as the verification path for every
    # reported number, so an undercount here is worse than an undercount in a
    # document: it certifies the wrong figure.
    hw = [r for r in rows if is_metered_arm(r)]
    lines += ["## Hardware rows [HW] and G0b proxy-fidelity gate", ""]
    if hw:
        ok = [r for r in hw if r.get("status") == "ok"]
        failed = [r for r in hw if r.get("status") != "ok"]
        spent = sum(r.get("metered_seconds") or 0.0 for r in ok)
        from collections import defaultdict as _dd
        by_arm = _dd(lambda: [0, 0.0])
        for r in ok:
            by_arm[r["arm"]][0] += 1
            by_arm[r["arm"]][1] += float(r.get("metered_seconds") or 0.0)
        breakdown = "; ".join(f"{a} {n} fits {sec:.1f} s" for a, (n, sec) in sorted(by_arm.items()))
        lines += [f"{len(ok)} successful fits, {len(failed)} failed, metered seconds recorded: {spent:.1f} "
                  f"(None-valued rows: {sum(1 for r in ok if r.get('metered_seconds') is None)})",
                  f"By arm: {breakdown}.", "",
                  "| Cell | Rows | Mean test AP | Mean val AP | Mean weight cosine (hw vs exact proxy) | Mean obj gap (hw - proxy) |",
                  "|---|---|---|---|---|---|"]
        # The fidelity table needs val_auprc and the fidelity block, which only
        # the paired proxy-vs-hardware cells carry. Select on the DATA rather
        # than on an arm name, so a future metered arm joins the campaign total
        # automatically and only enters this table if it actually has the
        # fidelity fields to populate it.
        cells = _dd(list)
        for r in ok:
            if "val_auprc" in r and isinstance(r.get("fidelity"), dict):
                cells[(r["config"], r["protocol"])].append(r)
        for key in sorted(cells):
            c = cells[key]
            gap = [r["fidelity"]["hw_objective_recomputed"] - r["fidelity"]["proxy_objective"] for r in c]
            lines.append(f"| {key[0]}/{key[1]} | {len(c)} | {np.mean([r['metrics']['auprc'] for r in c]):.4f} "
                         f"| {np.mean([r['val_auprc'] for r in c]):.4f} | {np.mean([r['fidelity']['weight_cosine'] for r in c]):.4f} "
                         f"| {np.mean(gap):+.4g} |")
        g0b = sorted([r for r in ok if r.get("block") == "G0b"], key=lambda r: r["config"])
        if len(g0b) >= 5:
            from scipy.stats import spearmanr
            px = [r["fidelity"]["proxy_val_auprc_same_pool"] for r in g0b]
            hv = [r["val_auprc"] for r in g0b]
            res = spearmanr(px, hv)
            rho = float(res.statistic)
            if not np.isfinite(rho):
                verdict = "UNSCOREABLE (constant input: Spearman undefined)"
            else:
                verdict = "PASS" if rho >= 0.5 else "FAIL"
            pval = float(res.pvalue) if np.isfinite(res.pvalue) else float("nan")
            lines += ["", f"G0b: Spearman(proxy val AP, hardware val AP) over {len(g0b)} configs = {rho:.3f} "
                      f"(p = {pval:.3f}; n=5, so the interval is wide) -> **{verdict}** (gate >= 0.5, prereg 3)"]
        else:
            lines += ["", f"G0b UNSCOREABLE YET: {len(g0b)}/5 hardware config fits present."]
    else:
        lines.append("No hardware rows yet (blocks pending team-lead approval / execution).")
    lines.append("")

    # ---- H1b on hardware (paired per-seed, identical splits) ----
    # DELIBERATELY exact, not startswith: H1b is a preregistered endpoint over
    # the B1 cells, and cvqboost_hw_mixed is a different arm (F32 mixed pool).
    # Widening this would silently change what the primary endpoint measures.
    hw_cells = {k: v for k, v in by_cell.items() if k[0] == "cvqboost_hw" and k[2] == "stratified"
                and len(v) >= N_SEEDS}   # B1 cells only; G0b cells are single-seed
    gbdt_matched = {a: {r["seed"]: r["metrics"]["auprc"] for r in by_cell.get((a, "matched13"), [])}
                    for a in ("xgboost", "lightgbm", "catboost")}
    hw_complete = {a: c for a, c in gbdt_matched.items() if len(c) >= N_SEEDS}
    if hw_cells and hw_complete:
        # selection on VALIDATION AP (repo-wide rule: A3, proxy-cell selection)
        best_hw = max(hw_cells, key=lambda k: np.mean([r["val_auprc"] for r in hw_cells[k]]))
        hwap = {r["seed"]: r["metrics"]["auprc"] for r in hw_cells[best_hw]}
        lines += ["", "### H1b on hardware [HW]"]
        for arm, c in hw_complete.items():
            seeds = sorted(set(hwap) & set(c))
            if len(seeds) < N_SEEDS:
                continue
            d = [hwap[s] - c[s] for s in seeds]
            ti = metrics.seed_mean_t_interval(d)
            neg = sum(1 for x in d if x < 0)
            lines.append(f"{best_hw[1]} minus {arm}/matched13: mean {ti['mean']:+.4f} "
                         f"CI [{ti['ci95'][0]:+.4f}, {ti['ci95'][1]:+.4f}], trails on {neg}/{len(d)} seeds, "
                         f"{'exceeds' if abs(ti['mean']) > MDE else 'within'} MDE {MDE} (A5)")
        # hardware vs its own exact proxy (H4 solver-fidelity component)
        hw_hashes = {r.get("config_hash") for r in hw_cells[best_hw]}
        matched_proxy = [k for k in by_cell if k[0] == "cvqboost_proxy"
                         and {r.get("config_hash") for r in by_cell[k]} & hw_hashes]
        if not matched_proxy:
            lines.append("H4 solver-fidelity component UNPAIRED: no proxy cell shares a "
                         f"config_hash with {best_hw[1]} (expected one; investigate).")
        for pk in matched_proxy:
            pxa = {r["seed"]: r["metrics"]["auprc"] for r in by_cell[pk]}
            seeds = sorted(set(hwap) & set(pxa))
            if len(seeds) >= N_SEEDS:
                d = [hwap[s] - pxa[s] for s in seeds]
                ti = metrics.seed_mean_t_interval(d)
                lines.append(f"{best_hw[1]} minus exact proxy {pk[1]}/{pk[2]}: mean {ti['mean']:+.4f} "
                             f"CI [{ti['ci95'][0]:+.4f}, {ti['ci95'][1]:+.4f}] (H4 solver-fidelity component; "
                             f"NOT the preregistered H4 controls)")
        lines.append("")

    # ---- A3 side-by-side ----
    lines += ["## A3 build side-by-side (validation AP, free config, dct pool)", ""]
    seq = {r["seed"]: r["val_auprc"] for r in
           by_cell.get(("cvqboost_proxy", "free", "dct", "sequential"), [])}
    ful = {r["seed"]: r["val_auprc"] for r in
           by_cell.get(("cvqboost_proxy", "free", "dct", "full"), [])}
    common = sorted(set(seq) & set(ful))
    if len(common) >= N_SEEDS:
        ms, mf = np.mean([seq[s] for s in common]), np.mean([ful[s] for s in common])
        pick = "full" if mf > ms else "sequential"
        lines += ["| Seed | sequential val AP | full-pair val AP |", "|---|---|---|"]
        lines += [f"| {s} | {seq[s]:.4f} | {ful[s]:.4f} |" for s in common]
        lines += ["", f"Mean: sequential {ms:.4f}, full-pair {mf:.4f} -> "
                  f"**A3 selection: {pick}** (chosen on validation only, before any "
                  "test-set comparison; applied uniformly to every CVQBoost cell)."]
    else:
        lines.append(f"UNSCOREABLE YET: {len(common)}/{N_SEEDS} paired seeds present "
                     f"(sequential {len(seq)}, full {len(ful)}).")
    lines.append("")

    # ---- budget equivalence ----
    lines += ["## Tuning Budget Equivalence (prereg 6; asymmetry reported as-is)", "",
              "| Study | Trials | CV AP | Wall seconds |", "|---|---|---|---|"]
    for k in sorted(tuned):
        t = tuned[k]
        lines.append(f"| {k} | {t['n_trials']} | {t['cv_ap']:.4f} | {t['wall_seconds']:.0f} |")
    lines += ["", "Model fits per GBDT trial: 5 folds x early-stopped fit. CVQBoost proxy "
              "fits are pool builds + classical solves (zero metered seconds).", ""]

    out = RESULTS_DIR / "gate_report.md"
    lines = _fit_table_widths(lines)
    out.write_text("\n".join(lines))
    print(f"gate_report.md written: {len(rows)} rows summarized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
