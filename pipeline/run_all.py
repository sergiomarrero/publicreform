"""Orchestrate the Stage 1 pipeline: fetch, normalize, validate, then write.

Order:
  1. Fetch UI ETA 9050, SNAP APT, and WIOA PY2023 at their requested vintages.
  2. Save downloaded source files under data/raw/ and record provenance in
     data/raw/SOURCES.json (URL, host served, timestamp, vintage).
  3. Normalize into the canonical 50 states + DC structure (territories flagged).
  4. Run the validation gate and write data/validation_report.json.
  5. Write data/states.json for the UI ONLY if every check passes. On failure,
     write data/states.preview.json instead so the structure can be inspected
     without publishing unverified numbers.

Run: python pipeline/run_all.py
Backfill a different vintage: pass arguments to the fetchers in code; each
fetcher takes a date or vintage parameter.
"""

from __future__ import annotations

import json
import os
import sys

# Allow running both as "python pipeline/run_all.py" and as a module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import normalize  # noqa: E402
import validate  # noqa: E402
from citations import write_citation_pointers  # noqa: E402
from fetch_snap_apt import fetch_snap_apt  # noqa: E402
from fetch_ui_eta9050 import fetch_ui_eta9050  # noqa: E402
from fetch_wioa_py2023 import fetch_wioa_py2023  # noqa: E402

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")


def write_sources_json(fetches: list) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, "SOURCES.json")
    payload = {
        "generated_at": normalize._utc_now(),
        "note": (
            "Provenance for every source fetch: URL, host that served the "
            "bytes, fetch timestamp, vintage, and whether the live host was "
            "blocked by the execution environment."
        ),
        "sources": {f.source_id: f.to_sources_entry() for f in fetches},
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return path


def main() -> int:
    print("Stage 1 pipeline: fetch -> normalize -> validate -> write\n")

    ui = fetch_ui_eta9050()
    snap = fetch_snap_apt(fiscal_year=2024)
    wioa = fetch_wioa_py2023(program_year=2023)

    for f in (ui, snap, wioa):
        flag = "BLOCKED" if f.blocked else "ok"
        print(f"  [{flag:7}] {f.source_id:11} vintage={f.vintage or f.requested_vintage} "
              f"rows={len(f.rows)}")
        for note in f.notes:
            print(f"             note: {note}")

    sources_path = write_sources_json([ui, snap, wioa])
    print(f"\n  wrote {sources_path}")

    citation_paths = write_citation_pointers(RAW_DIR)
    print(f"  wrote {len(citation_paths)} citation pointers to data/raw/citations/")

    dataset = normalize.build_dataset(ui, snap, wioa)

    report = validate.run_validation(ui, snap, wioa, dataset)
    print(f"  wrote data/validation_report.json")

    print("\nValidation gate:")
    for c in report["checks"]:
        print(f"  [{c['status']:7}] {c['id']:24} {c['detail']}")
    print(f"\n  summary: {report['summary']}  overall_pass={report['overall_pass']}")

    if report["overall_pass"]:
        out_path = os.path.join(DATA_DIR, "states.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(dataset, fh, indent=2)
        print(f"\n  gate PASSED. wrote {out_path} for the UI.")
        return 0

    preview_path = os.path.join(DATA_DIR, "states.preview.json")
    with open(preview_path, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=2)
    print(
        f"\n  gate did NOT pass. states.json withheld; wrote {preview_path} "
        f"for inspection only (not consumed by the UI)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
