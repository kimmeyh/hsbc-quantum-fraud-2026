"""Contract tests over results.json rows (Sprint 6 retro improvement 2).

Three schema defects shipped in one sprint, each a KeyError waiting in a
consumer rather than a value that was merely wrong:

- F32 rows set `config` but not `config_hash`; cost_analysis reads
  `r["config_hash"]` and would have raised when the operating-point table was
  regenerated. Found by reading the consumer, not by a test.
- F32 rows lacked `feature_set`; score_gates keys unknown arms by it, so the
  gate report could not regenerate. Found only when the suite ran.
- F32 rows lacked `pair_build`; same class.

A writer cannot be trusted to remember what every reader needs. These tests
assert the CONTRACT instead: every row carries the fields its consumers index
directly, so a new arm fails here rather than three steps downstream.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store

RESULTS = Path(__file__).resolve().parents[1] / "results" / "results.json"

# Fields every row must carry, whatever the arm.
UNIVERSAL = ("arm", "seed", "evidence_tag")

# Fields a consumer indexes with [] rather than .get(), so absence raises.
# score_gates keys unknown arms by feature_set; cost_analysis reads config_hash
# on every row and pair_build on cvqboost cells.
CONSUMER_INDEXED = ("config_hash",)

VALID_TAGS = {"HW", "SIM", "PROJ"}


def _rows():
    if not RESULTS.exists():
        pytest.skip("results.json not present")
    return json.loads(RESULTS.read_text())["rows"]


def test_every_row_has_the_universal_fields():
    missing = [
        (i, r.get("arm"), f)
        for i, r in enumerate(_rows())
        for f in UNIVERSAL
        if f not in r
    ]
    assert not missing, f"rows missing universal fields: {missing[:10]}"


def test_every_row_has_the_fields_consumers_index():
    """score_gates and cost_analysis use r[field], not r.get(field)."""
    missing = [
        (i, r.get("arm"), f)
        for i, r in enumerate(_rows())
        for f in CONSUMER_INDEXED
        if f not in r
    ]
    assert not missing, (
        f"rows missing consumer-indexed fields: {missing[:10]}. "
        "A row without these raises KeyError in score_gates or cost_analysis "
        "rather than being skipped, so the gate report cannot regenerate."
    )


def test_cvqboost_rows_carry_the_keys_their_consumers_group_by():
    """cost_analysis groups cvqboost cells by (arm, config, pool_variant) and
    reads pair_build; score_gates groups by (arm, config, protocol, pair_build).
    """
    bad = []
    for i, r in enumerate(_rows()):
        arm = str(r.get("arm", ""))
        if not arm.startswith("cvqboost"):
            continue
        for f in ("config", "pool_variant", "pair_build", "protocol"):
            if f not in r:
                bad.append((i, arm, f))
    assert not bad, f"cvqboost rows missing grouping keys: {bad[:10]}"


def test_evidence_tags_are_from_the_frozen_vocabulary():
    """The tag vocabulary is fixed by the preregistration; a typo silently
    excludes a row from every tag-filtered table."""
    bad = [(i, r.get("arm"), r.get("evidence_tag"))
           for i, r in enumerate(_rows())
           if r.get("evidence_tag") not in VALID_TAGS]
    assert not bad, f"rows with tags outside {VALID_TAGS}: {bad[:10]}"


def test_hardware_rows_account_for_their_spend():
    """A metered row that cannot say what it cost makes the spend guard blind
    (amendment A8). Unparseable billing must be CHARGED and FLAGGED, never absent.
    """
    bad = []
    for i, r in enumerate(_rows()):
        if r.get("evidence_tag") != "HW":
            continue
        if str(r.get("status", "")).startswith("ok"):
            if r.get("metered_seconds") is None:
                bad.append((i, r.get("arm"), "metered_seconds is None on an ok row"))
            # The audit flag arrived with amendment A8, so the 27 Sprint 4 rows
            # (blocks B1 and G0b) predate it. Their spend IS fully recorded --
            # 120.0 s, verified -- so this is a provenance gap in old rows, not
            # an accounting failure. Every block written since A8 must carry it.
            if r.get("block") not in ("B1", "G0b") and "metered_seconds_parsed" not in r:
                bad.append((i, r.get("arm"), "missing metered_seconds_parsed audit flag"))
    assert not bad, f"hardware rows with unaccounted spend: {bad[:10]}"


def test_prediction_paths_are_arm_keyed():
    """Amendment A9: hardware and its exact proxy deliberately share a
    config_hash, so keying predictions by hash alone let the proxy backfill
    OVERWRITE the hardware scores. The arm must change the path."""
    a = store.prediction_path("deadbeef", 42, "stratified", "cvqboost_hw")
    b = store.prediction_path("deadbeef", 42, "stratified", "cvqboost_proxy")
    assert a != b, "same path for two arms: the A9 collision would recur"


def test_metered_billing_takes_the_conservative_reading():
    """PR #36 Copilot finding. The F32 runner returned the FIRST device-usage
    value found depth-first; the frozen runner collects all matches and returns
    max(). A response nesting a per-sample runtime alongside a larger total
    would then under-charge _spent(), which is the single source of truth for
    the block cap, and a cap that under-counts is a cap that can be breached.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_hardware_f32 as f32

    # larger value nested deeper, as a per-sample list
    assert f32._metered({"job_info": {"job_result": {"device_usage_s": 4}},
                         "results": {"run_time": [9, 9, 9]}}) == 9.0
    # larger value at the shallower key
    assert f32._metered({"job_info": {"job_result": {"device_usage_s": 12}},
                         "results": {"run_time": [3]}}) == 12.0
    # the real F32 response shape still bills correctly
    assert f32._metered({"job_info": {"job_result": {"device_usage_s": 4}}}) == 4.0
    # unbillable stays None so the caller charges the conservative estimate
    assert f32._metered(object()) is None


def test_every_fold_builder_deduplicates():
    """PR #41 / amendment A17. The frozen protocol removes 1,081 exact duplicates
    BEFORE splitting. The exploratory pool modules were written as standalone
    code and called data.load_ulb() directly, training on 284,807 rows against
    every comparator's 283,726 -- invisible for two sprints because those arms
    were only compared against each other.

    Asserted on the SOURCE because the alternative is loading the 150MB dataset
    in a unit test; the check is narrow enough that a rename cannot silently
    defeat it (a fold builder that stops calling load_ulb no longer matches).
    """
    import re
    src_dir = Path(__file__).resolve().parent
    offenders = []
    for f in src_dir.glob("*.py"):
        if f.name.startswith("test_"):
            continue
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"data\.load_ulb\(\)", text):
            line_no = text[:m.start()].count("\n") + 1
            line = text.splitlines()[line_no - 1]
            # Two legitimate forms: chained .drop_duplicates(), or passed to the
            # _dedupe helper (run_classical, backfill_predictions). Anything else
            # splits on the raw 284,807 rows.
            if ".drop_duplicates" in line or "_dedupe(" in line:
                continue
            # run_classical's --smoke path subsamples before use and dedupes
            # downstream; it is the argparse entry point, not a fold builder.
            if f.name == "run_classical.py":
                continue
            offenders.append(f"{f.name}:{line_no}")
    assert not offenders, (
        "fold builders calling data.load_ulb() without .drop_duplicates(): "
        f"{offenders}. The protocol deduplicates before splitting; training on "
        "the duplicates inflates any metric by letting identical transactions "
        "appear in both train and test."
    )


def test_master_plan_keeps_its_required_sections():
    """A card-pruning script deleted the Targeted roadmap section twice.

    The prune walks from a shipped card's `**F##.` header to the next card
    header, and a `## ` section heading falling inside that span went with it.
    The loss was silent: the file still parsed, still listed cards, and nothing
    failed. It went unnoticed for a full sprint.
    """
    plan = Path(__file__).resolve().parents[2] / "docs" / "ALL_SPRINTS_MASTER_PLAN.md"
    if not plan.exists():
        pytest.skip("master plan not present")
    text = plan.read_text(encoding="utf-8")
    required = [
        "## Past Sprint Summary",
        "## Last Completed Sprint",
        "## Targeted roadmap",
        "## Next Sprint Candidates",
    ]
    missing = [h for h in required if h not in text]
    assert not missing, (
        f"master plan is missing required section(s): {missing}. A pruning "
        "script most likely deleted past a '## ' heading; recover from git "
        "history rather than rewriting from memory."
    )


def test_ieee_fold_builders_deduplicate():
    """Amendment A17 extended to the IEEE-CIS path (F3 Task A).

    Section 4 item 7 removes exact duplicates before splitting and reports the
    count PER DATASET. The ULB loaders do it; the Sprint 6 IEEE scaffolding did
    not, in code written in the same sprint and style as the three modules A17
    records. On IEEE-CIS the effect is nil -- 6 duplicate rows, none of them
    fraud -- but a protocol step is not optional because its effect is small,
    and "it would not have mattered" is only knowable after checking.
    """
    import re
    src_dir = Path(__file__).resolve().parent
    offenders = []
    for f in src_dir.glob("ieee_*.py"):
        if f.name.startswith("test_"):
            continue
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"data\.load_ieee_cis_train\(\)", text):
            line_no = text[:m.start()].count("\n") + 1
            lines = text.splitlines()
            # Look at the loading line AND the two after it: the deduplication
            # is often the next statement rather than a chained call, e.g.
            #     raw = data.load_ieee_cis_train()
            #     df, n = dedupe_ieee(raw)
            window = "\n".join(lines[line_no - 1:line_no + 2])
            if ".drop_duplicates" in window or "dedupe_ieee(" in window:
                continue
            # ieee_baseline is a LABELED scale check, explicitly not a protocol
            # run; its own docstring scopes the reduced recipe out.
            if f.name == "ieee_baseline.py":
                continue
            offenders.append(f"{f.name}:{line_no}")
    assert not offenders, (
        f"IEEE fold builders loading without deduplication: {offenders}. "
        "Route through ieee_loader.dedupe_ieee and report the count."
    )
