"""F46 step 1: report the Dirac-3 allocation balance. ZERO metered seconds.

`QciClient.get_allocations()` is a plain HTTP GET against the allocations
endpoint -- it submits no job, so it consumes no QPU time and needs no Criterion
H approval. Verified by reading the client source before calling it, rather than
assuming from the method name.

QCi's email of 2026-09-09 says 3,000 complimentary seconds were loaded. This
reads the number from the API instead of taking the email's word for it: the
account is what governs what we can run, and an email is a statement about it.

Never prints the token. The client reads QCI_API_URL and QCI_TOKEN from the
environment per ADR-0011.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys


def _load_env() -> None:
    p = pathlib.Path(__file__).resolve().parents[2] / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    _load_env()
    url, token = os.environ.get("QCI_API_URL"), os.environ.get("QCI_TOKEN")
    if not url or not token:
        print("QCI_API_URL and QCI_TOKEN must both be set (ADR-0011).")
        return 2

    from qci_client import QciClient

    client = QciClient(api_token=token, url=url)
    allocations = client.get_allocations()

    print(json.dumps(allocations, indent=2))

    # Pull the seconds out of whatever shape the response uses, without
    # asserting a schema we have not seen.
    def _walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from _walk(v, f"{path}[{i}]")
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            yield path, o

    print("\nnumeric fields:")
    for path, val in _walk(allocations):
        print(f"  {path:48} {val}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
