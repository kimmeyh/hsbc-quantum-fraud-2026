"""Convert British spellings to US English in tracked markdown.

EXCLUDED, and the exclusion is the important part:
  - docs/paper/*          the submitted proposal, appendix and cover letter
  - experiments/PREREGISTRATION.md   FROZEN, amendments only
  - docs/submission/*     the submitted package record

Those are frozen artefacts of a filing made 2026-09-12. Editing them would
change a document of record after the fact, which is worse than an inconsistent
spelling.

Proper nouns are protected: "Database Contents License" is a licence NAME and
keeps its own spelling; the DbCL is also already US-spelled, so only the
standalone word moves.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path("D:/Data/Harold/github/hsbc-quantum-fraud-2026")
if not (ROOT / ".git").exists():
    raise SystemExit(f"not a git repository: {ROOT}")

EXCLUDE_PREFIXES = ("docs/paper/", "docs/submission/")
EXCLUDE_FILES = ("experiments/PREREGISTRATION.md",)

# British -> US. Order matters only in that longer forms are listed first.
PAIRS = [
    ("behaviour", "behavior"), ("behaviours", "behaviors"),
    ("colour", "color"), ("colours", "colors"),
    ("favour", "favor"), ("favours", "favors"), ("favoured", "favored"),
    ("favourable", "favorable"), ("favourite", "favorite"),
    ("labour", "labor"), ("neighbour", "neighbor"), ("neighbours", "neighbors"),
    ("honour", "honor"), ("honoured", "honored"),
    ("rumour", "rumor"),
    ("organise", "organize"), ("organised", "organized"),
    ("organising", "organizing"), ("organisation", "organization"),
    ("organisations", "organizations"),
    ("recognise", "recognize"), ("recognised", "recognized"),
    ("recognising", "recognizing"),
    ("realise", "realize"), ("realised", "realized"),
    ("minimise", "minimize"), ("minimised", "minimized"),
    ("maximise", "maximize"), ("maximised", "maximized"),
    ("optimise", "optimize"), ("optimised", "optimized"),
    ("optimising", "optimizing"), ("optimisation", "optimization"),
    ("emphasise", "emphasize"), ("emphasised", "emphasized"),
    ("prioritise", "prioritize"), ("prioritised", "prioritized"),
    ("prioritising", "prioritizing"),
    ("summarise", "summarize"), ("summarised", "summarized"),
    ("categorise", "categorize"), ("categorised", "categorized"),
    ("apologise", "apologize"),
    ("analyse", "analyze"), ("analysed", "analyzed"), ("analysing", "analyzing"),
    ("paralyse", "paralyze"),
    ("centre", "center"), ("centres", "centers"), ("centred", "centered"),
    ("metre", "meter"), ("metres", "meters"),
    ("theatre", "theater"),
    ("licence", "license"), ("licences", "licenses"),
    ("defence", "defense"), ("offence", "offense"), ("pretence", "pretense"),
    ("travelling", "traveling"), ("travelled", "traveled"),
    ("modelling", "modeling"), ("modelled", "modeled"),
    ("labelling", "labeling"), ("labelled", "labeled"),
    ("cancelled", "canceled"), ("cancelling", "canceling"),
    ("signalling", "signaling"),
    ("fulfil", "fulfill"), ("fulfilment", "fulfillment"),
    ("enrol", "enroll"), ("skilful", "skillful"), ("wilful", "willful"),
    ("grey", "gray"),
    ("aluminium", "aluminum"),
    ("programme", "program"), ("programmes", "programs"),
    ("whilst", "while"), ("amongst", "among"),
    ("learnt", "learned"), ("spelt", "spelled"), ("burnt", "burned"),
    ("dreamt", "dreamed"),
    ("judgement", "judgment"), ("judgements", "judgments"),
    ("acknowledgement", "acknowledgment"),
    ("acknowledgements", "acknowledgments"),
    ("ageing", "aging"),
    ("cheque", "check"), ("storey", "story"), ("tyre", "tire"),
    ("kerb", "curb"), ("plough", "plow"), ("draught", "draft"),
    ("sceptical", "skeptical"), ("sceptic", "skeptic"),
    ("sceptics", "skeptics"), ("scepticism", "skepticism"),
    ("manoeuvre", "maneuver"),
    ("artefact", "artifact"), ("artefacts", "artifacts"),
    ("towards", "toward"),
    # ADDED 2026-09-17, synced with test_us_english.py after the team lead found
    # `memorise` and `specialised` in the explainer while the guard passed. The
    # original list covered the words the FIRST sweep happened to hit, which is
    # how a word list decays: it records the past rather than the class.
    ("optimise", "optimize"), ("optimised", "optimized"),
    ("optimising", "optimizing"), ("optimisation", "optimization"),
    ("optimiser", "optimizer"),
    ("generalise", "generalize"), ("generalised", "generalized"),
    ("generalising", "generalizing"),
    ("specialise", "specialize"), ("specialised", "specialized"),
    ("specialising", "specializing"),
    ("normalise", "normalize"), ("normalised", "normalized"),
    ("normalising", "normalizing"),
    ("utilise", "utilize"), ("utilised", "utilized"), ("utilising", "utilizing"),
    ("penalise", "penalize"), ("penalised", "penalized"),
    ("penalising", "penalizing"),
    ("characterise", "characterize"), ("characterised", "characterized"),
    ("characterising", "characterizing"),
    ("criticise", "criticize"), ("criticised", "criticized"),
    ("criticising", "criticizing"),
    ("memorise", "memorize"), ("memorised", "memorized"),
    ("memorising", "memorizing"),
    ("randomise", "randomize"), ("randomised", "randomized"),
    ("randomising", "randomizing"),
    ("standardise", "standardize"), ("standardised", "standardized"),
    ("standardising", "standardizing"),
    ("visualise", "visualize"), ("visualised", "visualized"),
    ("visualising", "visualizing"),
    ("practise", "practice"), ("practised", "practiced"),
    ("practising", "practicing"),
    ("flavour", "flavor"), ("flavours", "flavors"),
    ("rigour", "rigor"), ("vigour", "vigor"),
    ("endeavour", "endeavor"), ("saviour", "savior"),
    ("signalled", "signaled"), ("totalled", "totaled"),
    ("levelled", "leveled"), ("fuelled", "fueled"), ("marvelled", "marveled"),
    ("sizeable", "sizable"), ("moustache", "mustache"),
    ("mould", "mold"), ("smoulder", "smolder"),
]

# Spans that must never be rewritten, checked case-sensitively.
PROTECTED = (
    "Database Contents License",
    "Open Data Commons",
    # Direct quotation from the DbCL licence text. Never rewritten: changing a
    # spelling inside a quotation is a misquotation. Built by concatenation
    # because a literal newline in a source string is how this file was broken
    # when the span was first added.
    "do not exclude any field of" + chr(10) + "  endeavour.",
)


def match_case(src: str, repl: str) -> str:
    if src.isupper():
        return repl.upper()
    if src[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    files = []
    for rel in out.stdout.splitlines():
        if rel in EXCLUDE_FILES:
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        files.append(ROOT / rel)
    return files


def main() -> None:
    total = 0
    touched = []
    for path in tracked_markdown():
        text = path.read_text(encoding="utf-8")
        original = text

        # Mask protected spans so a replacement cannot reach inside them.
        masks: dict[str, str] = {}
        for i, span in enumerate(PROTECTED):
            token = f"\x00PROT{i}\x00"
            if span in text:
                masks[token] = span
                text = text.replace(span, token)

        count = 0
        for brit, us in PAIRS:
            pattern = re.compile(r"\b" + brit + r"\b", re.IGNORECASE)

            def sub(m: re.Match) -> str:
                nonlocal count
                count += 1
                return match_case(m.group(0), us)

            text = pattern.sub(sub, text)

        for token, span in masks.items():
            text = text.replace(token, span)

        if text != original:
            path.write_text(text, encoding="utf-8")
            rel = path.relative_to(ROOT)
            touched.append((str(rel), count))
            total += count

    for rel, n in sorted(touched, key=lambda x: -x[1]):
        print(f"{n:4d}  {rel}")
    print(f"\n{total} replacements across {len(touched)} files")


if __name__ == "__main__":
    main()
