"""Validation gate. Runs before any UI-facing JSON is written.

The gate compares freshly fetched values against the known-good anchors in
anchors.py and confirms jurisdiction coverage. It emits data/validation_report.json
summarizing pass, fail, or blocked per check and the vintage actually ingested.

A check is:
  pass    - value matched the anchor within tolerance, coverage satisfied
  fail    - value present but wrong (including a WIOA vintage mismatch)
  blocked - the source could not be fetched, so the claim cannot be verified

The gate passes only when every check is pass. fail or blocked stops the build;
states.json is not written. The pipeline never silently publishes.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import anchors
import states
from model import SourceFetch


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(check_id, source, vintage, status, detail, **extra):
    rec = {
        "id": check_id,
        "source": source,
        "vintage": vintage,
        "status": status,
        "detail": detail,
    }
    rec.update(extra)
    return rec


def _validate_snap(snap: SourceFetch) -> list[dict]:
    checks: list[dict] = []
    by_name = {r["name"]: r["snap_apt_timely"] for r in snap.rows}
    live_blocked = bool(snap.provenance.get("live_fetch_blocked"))
    verification_mode = (
        "transcription_consistency" if live_blocked else "independent_source"
    )

    if not snap.rows:
        checks.append(
            _check("snap_present", "snap_apt", snap.vintage, "blocked",
                   "No SNAP APT rows fetched.")
        )
        return checks

    checks.append(
        _check("snap_present", "snap_apt", snap.vintage, "pass",
               f"{len(snap.rows)} SNAP APT rows parsed.")
    )

    # Spot anchors.
    spot_fail = []
    for name, expected in anchors.SNAP_SPOT_ANCHORS.items():
        got = by_name.get(name)
        if got is None or abs(got - expected) > anchors.SNAP_TOLERANCE:
            spot_fail.append(f"{name}: expected {expected}, got {got}")
    checks.append(
        _check(
            "snap_spot_anchors", "snap_apt", snap.vintage,
            "pass" if not spot_fail else "fail",
            "All spot anchors matched." if not spot_fail
            else "Spot anchor mismatch: " + "; ".join(spot_fail),
            verification_mode=verification_mode,
        )
    )

    # Published max and min.
    max_name = max(by_name, key=by_name.get)
    min_name = min(by_name, key=by_name.get)
    exp_max_name, exp_max_val = anchors.SNAP_PUBLISHED_MAX
    exp_min_name, exp_min_val = anchors.SNAP_PUBLISHED_MIN
    extremes_ok = (
        max_name == exp_max_name
        and abs(by_name[max_name] - exp_max_val) <= anchors.SNAP_TOLERANCE
        and min_name == exp_min_name
        and abs(by_name[min_name] - exp_min_val) <= anchors.SNAP_TOLERANCE
    )
    checks.append(
        _check(
            "snap_extremes", "snap_apt", snap.vintage,
            "pass" if extremes_ok else "fail",
            f"max={max_name} {by_name[max_name]}, min={min_name} {by_name[min_name]}",
            verification_mode=verification_mode,
        )
    )

    # Ranking-jurisdiction coverage within SNAP (territories are extra).
    covered = {states.normalize_code(n) for n in by_name}
    missing = [c for c in states.ranking_codes() if c not in covered]
    checks.append(
        _check(
            "snap_ranking_coverage", "snap_apt", snap.vintage,
            "pass" if not missing else "fail",
            "All 51 ranking jurisdictions present in SNAP table."
            if not missing else f"Missing from SNAP: {missing}",
        )
    )
    return checks


def _validate_wioa(wioa: SourceFetch) -> list[dict]:
    checks: list[dict] = []
    national = wioa.national or {}

    if not national:
        checks.append(
            _check(
                "wioa_vintage", "wioa", wioa.vintage, "blocked",
                "No WIOA national headline figures available to confirm the "
                "PY2023 vintage. The DOL host is blocked and the brief carries "
                "national figures for reference only, not a fetched state table.",
            )
        )
    else:
        adult_q2 = national.get("adult", {}).get("emp_q2")
        dw_earn = national.get("dislocated_worker", {}).get("median_earnings_q2")
        matches_py2023 = (
            adult_q2 is not None
            and abs(adult_q2 - anchors.WIOA_ANCHOR_ADULT_EMP_Q2)
            <= anchors.WIOA_PCT_TOLERANCE
            and dw_earn is not None
            and abs(dw_earn - anchors.WIOA_ANCHOR_DW_MEDIAN_EARNINGS)
            <= anchors.WIOA_EARNINGS_TOLERANCE
        )
        py2024_adult = anchors.WIOA_PY2024_NATIONAL["adult"]["emp_q2"]
        py2024_dw = anchors.WIOA_PY2024_NATIONAL["dislocated_worker"][
            "median_earnings_q2"
        ]
        matches_py2024 = (
            adult_q2 is not None
            and abs(adult_q2 - py2024_adult) <= anchors.WIOA_PCT_TOLERANCE
            and dw_earn is not None
            and abs(dw_earn - py2024_dw) <= anchors.WIOA_EARNINGS_TOLERANCE
        )
        if matches_py2023:
            checks.append(
                _check("wioa_vintage", "wioa", "PY2023", "pass",
                       f"PY2023 anchors matched: Adult Q2 {adult_q2}%, "
                       f"DW median earnings ${dw_earn}.")
            )
        elif matches_py2024:
            checks.append(
                _check("wioa_vintage", "wioa", wioa.vintage, "fail",
                       "WIOA vintage mismatch: looks like PY2024, expected "
                       "PY2023.")
            )
        else:
            checks.append(
                _check("wioa_vintage", "wioa", wioa.vintage, "fail",
                       f"WIOA national figures matched neither PY2023 nor "
                       f"PY2024 anchors: Adult Q2 {adult_q2}, DW median {dw_earn}.")
            )

    if not wioa.rows:
        checks.append(
            _check("wioa_state_coverage", "wioa", wioa.vintage, "blocked",
                   "No WIOA state rows fetched.")
        )
    else:
        covered = {r["code"] for r in wioa.rows}
        missing = [c for c in states.ranking_codes() if c not in covered]
        checks.append(
            _check("wioa_state_coverage", "wioa", wioa.vintage,
                   "pass" if not missing else "fail",
                   "All 51 ranking jurisdictions present in WIOA table."
                   if not missing else f"Missing from WIOA: {missing}")
        )
    return checks


def _validate_ui(ui: SourceFetch) -> list[dict]:
    checks: list[dict] = []
    if not ui.rows:
        checks.append(
            _check("ui_present", "ui_eta9050", ui.vintage, "blocked",
                   "No ETA 9050 rows fetched.")
        )
        return checks

    checks.append(
        _check("ui_present", "ui_eta9050", ui.vintage, "pass",
               f"{len(ui.rows)} ETA 9050 rows parsed.")
    )

    by_code = {r["code"]: r["ui_first_pay_14_21"] for r in ui.rows}
    out_of_range = [
        f"{c}={v}" for c, v in by_code.items() if v is None or not 0 <= v <= 100
    ]
    checks.append(
        _check("ui_range", "ui_eta9050", ui.vintage,
               "pass" if not out_of_range else "fail",
               "All UI values within 0 to 100."
               if not out_of_range else f"Out of range: {out_of_range}")
    )

    missing = [c for c in states.ranking_codes() if c not in by_code]
    checks.append(
        _check("ui_coverage", "ui_eta9050", ui.vintage,
               "pass" if not missing else "fail",
               "All 51 ranking jurisdictions present in ETA 9050."
               if not missing else f"Missing from UI: {missing}")
    )
    return checks


def _validate_ui_render_coverage(dataset: dict) -> dict:
    """The spec's explicit gate: all 51 jurisdictions present for UI, with the
    UI within-14/21 metric populated.
    """
    ranking = set(states.ranking_codes())
    present = {
        s["code"]
        for s in dataset["states"]
        if s["code"] in ranking
        and s["metrics"]["ui_first_pay_14_21"]["value"] is not None
    }
    missing = sorted(ranking - present)
    return _check(
        "ui_render_coverage_51", "ui_eta9050",
        dataset["metrics"]["ui_first_pay_14_21"].get("vintage"),
        "pass" if not missing else "blocked" if len(missing) == len(ranking)
        else "fail",
        "All 51 jurisdictions present with a UI metric value."
        if not missing
        else f"{len(missing)} of 51 jurisdictions lack a UI value: {missing}",
    )


def run_validation(
    ui: SourceFetch,
    snap: SourceFetch,
    wioa: SourceFetch,
    dataset: dict,
    report_path: str = "data/validation_report.json",
) -> dict:
    """Run all checks, write the report, and return it (with overall_pass)."""
    checks: list[dict] = []
    checks += _validate_ui(ui)
    checks += _validate_snap(snap)
    checks += _validate_wioa(wioa)
    checks.append(_validate_ui_render_coverage(dataset))

    overall_pass = all(c["status"] == "pass" for c in checks)
    counts = {
        "pass": sum(1 for c in checks if c["status"] == "pass"),
        "fail": sum(1 for c in checks if c["status"] == "fail"),
        "blocked": sum(1 for c in checks if c["status"] == "blocked"),
    }

    report = {
        "generated_at": _utc_now(),
        "gate": "stage1_pre_ui",
        "overall_pass": overall_pass,
        "summary": counts,
        "ingested_vintages": {
            "ui_eta9050": ui.vintage or ui.requested_vintage,
            "snap_apt": snap.vintage or snap.requested_vintage,
            "wioa": wioa.vintage or wioa.requested_vintage,
        },
        "checks": checks,
        "notes": _report_notes(ui, snap, wioa, overall_pass),
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    return report


def _report_notes(ui, snap, wioa, overall_pass) -> list[str]:
    notes = []
    if not overall_pass:
        notes.append(
            "Gate did not pass. data/states.json is intentionally not written "
            "for UI consumption until every check passes."
        )
    for fetch in (ui, snap, wioa):
        if fetch.provenance.get("live_fetch_blocked"):
            notes.append(
                f"{fetch.source_id}: live host blocked by environment network "
                f"policy; see SOURCES.json for attempts."
            )
    return notes
