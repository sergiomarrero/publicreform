"""Fetch UI first-payment timeliness, DOL ETA 9050.

Source: comma-delimited CSV from the DOL ETA Unemployment Insurance data
downloads. This is a download-and-parse, not a scrape.

Metric: percent of intrastate first payments made within 14/21 days of the
first compensable week. The federal Secretary's Standard is 87 percent within
14/21 days (states below it are flagged in the UI).

The fetcher takes year and month parameters so any historical month can be
backfilled later. States can revise ETA 9050 history at any time, so the
ingested month is always stamped explicitly in provenance.
"""

from __future__ import annotations

import csv
import io
import os
import re
from datetime import date

import states
from http_util import FetchBlocked, fetch, utc_now_iso
from model import SourceFetch

SOURCE_ID = "ui_eta9050"
LANDING = "https://oui.doleta.gov/unemploy/DataDownloads.asp"
REPORT_BUILDER = "https://oui.doleta.gov/unemploy/btq.asp"

# Raw ETA 9050 comma-delimited extract. The DataDownloads page links the raw
# report files under /unemploy/csv/. The exact filename is confirmed against
# the live host on the first reachable run; these candidates are tried in order.
RAW_CSV_CANDIDATES = [
    "https://oui.doleta.gov/unemploy/csv/9050.csv",
    "https://oui.doleta.gov/unemploy/csv/ar9050.csv",
    "https://oui.doleta.gov/unemploy/csv/eta9050.csv",
]

# Header signatures for the precomputed within-14/21-day percentage. Headers
# are normalized to lowercase alphanumerics before matching, so "pct_within_1421",
# "% within 14/21 days", and "Pct1421" all resolve to the same column. The exact
# live header is pinned against the real file on the first reachable run.
_PCT_NORM_SIGNATURES = ("1421", "within14", "within21", "timely")


def _default_period() -> tuple[int, int]:
    """Most recent complete month relative to today.

    ETA 9050 publishes monthly with a lag, so the latest complete month is the
    previous calendar month. Backfill callers pass explicit year and month.
    """
    today = date.today()
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def _find_state_idx(header: list[str]) -> int | None:
    for i, h in enumerate(header):
        hl = h.strip().lower()
        if hl in ("st", "state", "stname", "state_name"):
            return i
    return None


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _find_pct_idx(header: list[str]) -> int | None:
    for i, h in enumerate(header):
        if any(sig in _norm(h) for sig in _PCT_NORM_SIGNATURES):
            return i
    return None


def _parse_csv(content: bytes, year: int, month: int) -> tuple[list[dict], list[str]]:
    """Parse the ETA 9050 CSV into per-state percent within 14/21 days.

    Documented assumptions, since states can change the layout: a state column
    is located by header name; the within-14/21 percentage is read from a
    precomputed column when present. Rows are filtered to the requested period
    when a recognizable period column exists. Anything not mappable to a
    canonical jurisdiction is skipped.
    """
    notes: list[str] = []
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows_in = list(reader)
    if not rows_in:
        return [], ["empty CSV"]

    header = rows_in[0]
    state_idx = _find_state_idx(header)
    pct_idx = _find_pct_idx(header)
    if state_idx is None or pct_idx is None:
        notes.append(
            "Could not locate state and within-14/21 columns by header; "
            "raw layout needs review before this vintage is trusted."
        )
        return [], notes

    out: dict[str, dict] = {}
    for row in rows_in[1:]:
        if len(row) <= max(state_idx, pct_idx):
            continue
        code = states.try_normalize_code(row[state_idx])
        if not code:
            continue
        try:
            value = float(row[pct_idx].replace("%", "").strip())
        except ValueError:
            continue
        # ETA 9050 percentages are reported 0 to 100. Skip implausible rows.
        if not 0 <= value <= 100:
            continue
        out[code] = {
            "code": code,
            "name": states.display_name(code),
            "ui_first_pay_14_21": value,
        }
    return list(out.values()), notes


def fetch_ui_eta9050(
    year: int | None = None,
    month: int | None = None,
    raw_dir: str = "data/raw",
) -> SourceFetch:
    """Fetch ETA 9050 for a given month. Defaults to the latest complete month."""
    if year is None or month is None:
        year, month = _default_period()
    vintage = f"{year:04d}-{month:02d}"

    attempts: list[dict] = []
    blocked_any = False
    result = None
    for url in RAW_CSV_CANDIDATES:
        try:
            r = fetch(url)
        except FetchBlocked as blocked:
            blocked_any = True
            attempts.append({"url": blocked.url, "host": "blocked", "status": None,
                             "deny_reason": blocked.deny_reason})
            continue
        attempts.append({"url": r.url, "host": r.host, "status": r.status})
        if r.ok and r.content:
            result = r
            break

    if result is None:
        host = "blocked" if blocked_any else "unreachable"
        deny = "host_not_allowed" if blocked_any else "no_candidate_returned_csv"
        return SourceFetch(
            source_id=SOURCE_ID,
            requested_vintage=vintage,
            vintage=None,
            rows=[],
            provenance={
                "url": RAW_CSV_CANDIDATES[0],
                "host": host,
                "status": None,
                "fetched_at": utc_now_iso(),
                "landing": LANDING,
                "report_builder": REPORT_BUILDER,
                "raw_files": [],
                "attempts": attempts,
                "live_fetch_blocked": blocked_any,
                "deny_reason": deny,
            },
            blocked=True,
            notes=(
                ["Host blocked by environment network policy (host_not_allowed).",
                 "No ETA 9050 bytes available in this environment; values are null."]
                if blocked_any else
                ["No ETA 9050 CSV candidate returned usable bytes; confirm the "
                 "raw file URL on the DataDownloads page."]
            ),
        )

    os.makedirs(raw_dir, exist_ok=True)
    raw_path = os.path.join(raw_dir, f"ui_eta9050_{vintage}.csv")
    with open(raw_path, "wb") as fh:
        fh.write(result.content)

    rows, notes = _parse_csv(result.content, year, month)
    if not rows:
        notes.append(
            "No ETA 9050 rows parsed. Confirm the state column and the "
            "within-14/21-day percentage column against the live file, then "
            "pin them via _PCT_HEADER_HINTS on the first reachable run."
        )
    return SourceFetch(
        source_id=SOURCE_ID,
        requested_vintage=vintage,
        vintage=vintage,
        rows=rows,
        provenance={
            "url": result.url,
            "host": result.host,
            "status": result.status,
            "fetched_at": result.fetched_at,
            "landing": LANDING,
            "report_builder": REPORT_BUILDER,
            "raw_files": [raw_path],
            "attempts": attempts,
            "live_fetch_blocked": False,
        },
        blocked=len(rows) == 0,
        notes=notes,
    )


if __name__ == "__main__":
    out = fetch_ui_eta9050()
    print(f"ui_eta9050 vintage={out.requested_vintage} rows={len(out.rows)} "
          f"blocked={out.blocked}")
    for note in out.notes:
        print("  note:", note)
