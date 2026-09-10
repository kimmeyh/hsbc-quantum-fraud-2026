"""Where Dirac-3 QPU time comes from, and how to estimate it before spending it.

WHY THIS EXISTS. The F46 probe recorded 5.0 metered seconds because
`run_hardware.py` scrapes `device_usage_s` from the response repr, that field is
absent on the paid tier, and the code fell back to a default. The allocation
balance said 10. A default presented as a measurement is the same class of
defect as the stale 0.26 GAM figure: a number in the record that nothing checked.

THE BILLING RULE, validated:

    billed_seconds = ceil( sum(device.samples.runtime) )

Preprocessing is NOT billed. Only sample runtime is, rounded UP to whole
seconds. Team-lead hypothesis, tested against all 27 retained free-tier jobs: it
reproduces the total (120s) AND the per-job distribution (15 jobs at 4.0s, 12 at
5.0s) exactly. Rules that FAIL: floor of the same sum (93s), round (107s), and
every variant including preprocessing (103/113/130) or using the device span
(115/141/142).

Cross-checked on the paid tier: the F46 probe cost 10s by allocation balance,
implying sum(runtime) in (9, 10] over 8 samples, or 1.13-1.25 s/sample against
0.49 s/sample for the 91-variable free-tier jobs. A 1.15x variable increase
raised per-sample cost about 2.4x, so COST SCALES STEEPLY WITH PROBLEM SIZE.
That matches the team lead's observed ranges: degree-3 Fourier Wall calls 26-35s
against 5-10s for smaller degree-2 work, and some calls under 2s.

WHERE TO READ IT. `get_job_metrics(job_id)` carries a `device` section the
response repr does not:

    time_ns.device.<device>.samples.preprocessing_time    one per job
    time_ns.device.<device>.samples.runtime[i]            one per SAMPLE

Scrape nothing from a repr. The paid tier already changed that text once.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass

RESULTS = pathlib.Path(__file__).resolve().parents[1] / "results"
LEDGER = RESULTS / "qpu_cost_ledger.json"


@dataclass
class JobCost:
    """One job's measured cost, decomposed into its billed and unbilled parts."""
    job_id: str
    n_samples: int
    preprocessing_s: float      # measured but NOT billed
    runtime_sum_s: float        # the billed quantity, before rounding
    device_span_s: float
    billed_s: float             # ceil(runtime_sum_s)

    @property
    def per_sample_s(self) -> float:
        return self.runtime_sum_s / self.n_samples if self.n_samples else 0.0


def cost_from_metrics(job_id: str, metrics: dict) -> JobCost | None:
    """Decompose one job's metrics. None if the device section is absent.

    The device key is looked up rather than hardcoded -- it is
    'dirac-3_normalized_qudit' today, and a different device or mode changes it.
    Hardcoding a response shape is what broke the repr scrape.
    """
    try:
        dev_all = metrics["job_metrics"]["time_ns"]["device"]
    except (KeyError, TypeError):
        return None
    if not dev_all:
        return None
    samples = next(iter(dev_all.values())).get("samples", {})
    rt = samples.get("runtime") or []
    if not rt:
        return None
    runtime_sum = sum(rt) / 1e9
    return JobCost(
        job_id=job_id,
        n_samples=len(rt),
        preprocessing_s=samples.get("preprocessing_time", 0) / 1e9,
        runtime_sum_s=runtime_sum,
        device_span_s=(samples.get("end", 0) - samples.get("start", 0)) / 1e9,
        billed_s=float(math.ceil(runtime_sum)),
    )


def billed_from_runtime(runtime_sum_s: float) -> float:
    """The validated rule, in one place so nothing re-derives it."""
    return float(math.ceil(runtime_sum_s))


def estimate(n_samples: int, per_sample_s: float) -> float:
    """Predicted billed seconds for a comparable configuration.

    per_sample_s must come from a MEASURED call at similar degree and variable
    count, because the scaling is steep. Known anchors:

        91 variables,  degree 2, free tier : 0.49 s/sample
        105 variables, degree 2, paid tier : 1.13-1.25 s/sample

    Criterion H asks for expected seconds before approval, and the F46 probe was
    approved at "0-5s" and cost 10. An estimate outside its anchors should be
    stated as a range with its basis, not as a point.
    """
    return billed_from_runtime(n_samples * per_sample_s)


def anchors(ledger: dict | None = None) -> list[dict]:
    """Measured (size, cost) points available for estimating a new call."""
    led = ledger if ledger is not None else load_ledger()
    return [c for c in led.get("calls", []) if c.get("per_sample_s")]


def estimate_for(n_variables: int, degree: int, n_samples: int,
                 ledger: dict | None = None) -> dict:
    """Range estimate from history, or an honest 'unknown'.

    Returns a range rather than a point. With no comparable anchor it says so,
    so a Criterion H request can bound the block by call count instead of
    quoting a number nothing supports.
    """
    obs = [c for c in anchors(ledger)
           if c.get("degree") == degree
           and c.get("n_variables")
           and 0.5 <= c["n_variables"] / n_variables <= 2.0]
    if not obs:
        return {"known": False,
                "note": (f"no measured call at degree {degree} within 2x of "
                         f"{n_variables} variables; bound the block by call count "
                         f"and state the estimate as unknown")}
    per = sorted(c["per_sample_s"] for c in obs)
    return {"known": True, "n_anchors": len(obs),
            "low_s": estimate(n_samples, per[0]),
            "high_s": estimate(n_samples, per[-1]),
            "basis": f"{len(obs)} measured call(s), degree {degree}, within 2x size"}


def summarise(costs: list[JobCost]) -> dict:
    if not costs:
        return {}
    per = sorted(c.per_sample_s for c in costs)
    billed = [c.billed_s for c in costs]
    return {
        "n_jobs": len(costs),
        "total_billed_s": sum(billed),
        "billed_min": min(billed),
        "billed_max": max(billed),
        "per_sample_s_median": per[len(per) // 2],
        "per_sample_s_min": per[0],
        "per_sample_s_max": per[-1],
        "samples_seen": sorted({c.n_samples for c in costs}),
    }


def load_ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}
