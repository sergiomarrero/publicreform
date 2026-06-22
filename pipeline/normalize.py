"""Normalize the three fetched sources into one canonical structure.

Output is the shape the React app consumes: one record per jurisdiction, raw
values with units, every value carrying a source and vintage label, missing
values represented as explicit nulls with a reason. Nothing is pre-blended or
pre-scored; the composite index is deferred to a later stage.

This module builds the structure only. It does not write any UI-facing JSON;
run_all writes data/states.json only after the validation gate passes.
"""

from __future__ import annotations

from datetime import datetime, timezone

import states
from anchors import (
    SNAP_CORRECTIVE_ACTION_THRESHOLD,
    UI_SECRETARYS_STANDARD,
)
from model import SourceFetch

# Metric registry. Each entry feeds a column header tooltip in the UI:
# definition, source, agency, vintage, unit, direction, and any federal
# threshold. Vintage and availability are filled from the live fetch results.
METRIC_REGISTRY = {
    "ui_first_pay_14_21": {
        "label": "UI first payments within 14/21 days",
        "short_label": "UI % within 14/21 days",
        "definition": (
            "Percent of intrastate unemployment insurance first payments made "
            "within 14/21 days of the first compensable week."
        ),
        "agency": "DOL Employment and Training Administration",
        "source_name": "ETA 9050 First Payment Time Lapse",
        "primary_url": "https://oui.doleta.gov/unemploy/DataDownloads.asp",
        "unit": "percent",
        "direction": "higher_is_better",
        "threshold": UI_SECRETARYS_STANDARD,
        "threshold_label": "Federal Secretary's Standard: 87% within 14/21 days",
        "dimension": "speed",
        "source_id": "ui_eta9050",
    },
    "snap_apt_timely": {
        "label": "SNAP applications processed timely",
        "short_label": "SNAP APT % timely",
        "definition": (
            "Percent of SNAP applications processed timely, within 30 days for "
            "regular applications and 7 days for expedited, from the SNAP "
            "Quality Control active-case sample."
        ),
        "agency": "USDA Food and Nutrition Service",
        "source_name": "SNAP Application Processing Timeliness (APT)",
        "primary_url": "https://www.fns.usda.gov/snap/qc/timeliness",
        "unit": "percent",
        "direction": "higher_is_better",
        "threshold": SNAP_CORRECTIVE_ACTION_THRESHOLD,
        "threshold_label": "Corrective-action threshold: 90% timely",
        "dimension": "speed",
        "source_id": "snap_apt",
    },
    "wioa_adult_emp_q2": {
        "label": "WIOA Adult employment rate, Q2 after exit",
        "short_label": "WIOA Adult Q2 employment %",
        "definition": (
            "WIOA Title I Adult employment rate in the second quarter after "
            "program exit."
        ),
        "agency": "DOL Employment and Training Administration",
        "source_name": "WIOA State Performance (ETA-9169)",
        "primary_url": "https://www.dol.gov/agencies/eta/performance/results-archive",
        "unit": "percent",
        "direction": "higher_is_better",
        "threshold": None,
        "threshold_label": None,
        "dimension": "speed",
        "source_id": "wioa",
    },
    "wioa_adult_median_earnings_q2": {
        "label": "WIOA Adult median earnings, Q2 after exit",
        "short_label": "WIOA Adult median earnings",
        "definition": (
            "WIOA Title I Adult median earnings in the second quarter after "
            "program exit, in dollars."
        ),
        "agency": "DOL Employment and Training Administration",
        "source_name": "WIOA State Performance (ETA-9169)",
        "primary_url": "https://www.dol.gov/agencies/eta/performance/results-archive",
        "unit": "usd",
        "direction": "higher_is_better",
        "threshold": None,
        "threshold_label": None,
        "dimension": "outcome",
        "source_id": "wioa",
    },
    "wioa_adult_credential": {
        "label": "WIOA Adult credential attainment rate",
        "short_label": "WIOA credential %",
        "definition": (
            "WIOA Title I Adult credential attainment rate."
        ),
        "agency": "DOL Employment and Training Administration",
        "source_name": "WIOA State Performance (ETA-9169)",
        "primary_url": "https://www.dol.gov/agencies/eta/performance/results-archive",
        "unit": "percent",
        "direction": "higher_is_better",
        "threshold": None,
        "threshold_label": None,
        "dimension": "outcome",
        "source_id": "wioa",
    },
}

# Which metric keys come from which source, for null-reason attribution.
_METRICS_BY_SOURCE = {
    "ui_eta9050": ["ui_first_pay_14_21"],
    "snap_apt": ["snap_apt_timely"],
    "wioa": [
        "wioa_adult_emp_q2",
        "wioa_adult_median_earnings_q2",
        "wioa_adult_credential",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_reason(fetch: SourceFetch) -> str:
    prov = fetch.provenance or {}
    if prov.get("live_fetch_blocked"):
        return "source_host_blocked_by_network_policy"
    if fetch.blocked:
        return "source_unavailable_at_fetch_time"
    return "not_reported_by_source"


def _metric_vintage(fetch: SourceFetch) -> str | None:
    return fetch.vintage


def build_dataset(
    ui: SourceFetch, snap: SourceFetch, wioa: SourceFetch
) -> dict:
    """Merge the three fetches into the canonical dataset structure."""
    fetches = {"ui_eta9050": ui, "snap_apt": snap, "wioa": wioa}
    by_source_rows = {sid: f.by_code() for sid, f in fetches.items()}

    # Metric registry with live vintage and availability stamped in.
    metrics_meta: dict[str, dict] = {}
    for key, meta in METRIC_REGISTRY.items():
        fetch = fetches[meta["source_id"]]
        entry = dict(meta)
        entry["vintage"] = _metric_vintage(fetch)
        # available reflects whether there is data to render for this metric,
        # independent of whether the live host was reachable. live_fetch_blocked
        # records the provenance caveat separately so the UI can surface it.
        entry["available"] = bool(fetch.rows)
        entry["live_fetch_blocked"] = bool(
            fetch.provenance.get("live_fetch_blocked")
        )
        entry["source_label"] = _source_label(meta, fetch)
        metrics_meta[key] = entry

    state_records: list[dict] = []
    for code in states.all_codes():
        name = states.display_name(code)
        excluded = states.is_territory(code)
        metric_values: dict[str, dict] = {}
        for key, meta in METRIC_REGISTRY.items():
            sid = meta["source_id"]
            fetch = fetches[sid]
            row = by_source_rows[sid].get(code)
            value = row.get(key) if row else None
            null_reason = None
            if value is None:
                null_reason = _blocked_reason(fetch)
            metric_values[key] = {
                "value": value,
                "unit": meta["unit"],
                "vintage": _metric_vintage(fetch),
                "source": metrics_meta[key]["source_label"],
                "null_reason": null_reason,
            }

        flags = _compute_flags(metric_values, excluded)
        state_records.append(
            {
                "code": code,
                "name": name,
                "excluded_from_ranking": excluded,
                "metrics": metric_values,
                "flags": flags,
            }
        )

    dataset = {
        "meta": {
            "generated_at": _utc_now(),
            "version": "v1",
            "scope": (
                "Ranked and compared views cover 50 states plus DC (51 "
                "jurisdictions). Territories are shown where data exists and "
                "are excluded from ranking."
            ),
            "ranking_jurisdiction_count": len(states.ranking_codes()),
            "interpretation": (
                "This dashboard is descriptive and correlational. It shows "
                "variation in administrative performance across jurisdictions. "
                "It does not claim that administration causes mobility outcomes."
            ),
            "composite_index": {
                "status": "deferred",
                "note": (
                    "A blended 0-100 composite index is planned for a later "
                    "stage. v1 shows raw metrics only; no score is computed."
                ),
            },
        },
        "metrics": metrics_meta,
        "states": state_records,
        "sources": [f.to_sources_entry() for f in fetches.values()],
    }
    return dataset


def _source_label(meta: dict, fetch: SourceFetch) -> str:
    """Human-readable source and vintage label, for example
    'SNAP APT, FY2024, USDA FNS'. Falls back cleanly when blocked.
    """
    vintage = fetch.vintage or fetch.requested_vintage
    return f"{meta['source_name']}, {vintage}, {meta['agency']}"


def _compute_flags(metric_values: dict, excluded: bool) -> dict:
    """Federal-standard flags. Null when the underlying value is missing."""
    snap = metric_values["snap_apt_timely"]["value"]
    ui = metric_values["ui_first_pay_14_21"]["value"]
    return {
        "snap_below_corrective_action": (
            None if snap is None else snap < SNAP_CORRECTIVE_ACTION_THRESHOLD
        ),
        "ui_below_secretarys_standard": (
            None if ui is None else ui < UI_SECRETARYS_STANDARD
        ),
        "excluded_from_ranking": excluded,
    }
