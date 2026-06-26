"""Fetch SNAP Application Processing Timeliness (APT), USDA FNS.

Source: HTML table at the FNS timeliness pages. The agency was renamed from
Food and Nutrition Service (fns.usda.gov) to Food and Nutrition Administration
(fna.usda.gov) on June 1, 2026, so this fetcher tries fns first and falls back
to fna, logging which host actually served the data.

The fetcher takes a fiscal_year parameter so earlier vintages can be backfilled
later without a rewrite (apt-fy24, apt-fy23, and so on).

Metric: percent of applications processed timely (30-day regular, 7-day
expedited). Corrective-action threshold is 90 percent.
"""

from __future__ import annotations

import csv
import io
import os

from bs4 import BeautifulSoup

import anchors
import states
from http_util import FetchBlocked, fetch, utc_now_iso
from manual import find_manual
from model import SourceFetch

SOURCE_ID = "snap_apt"
LANDING = "https://www.fns.usda.gov/snap/qc/timeliness"


def _page_paths(fiscal_year: int) -> list[str]:
    """Candidate URLs for a fiscal year across both agency hosts.

    Order matters: fns first (historical host), then fna (post-rename host).
    """
    yy = fiscal_year % 100
    path = f"/snap/qc/timeliness/apt-fy{yy:02d}"
    return [
        f"https://www.fns.usda.gov{path}",
        f"https://www.fna.usda.gov{path}",
    ]


def _parse_html_table(html: bytes, fiscal_year: int) -> list[dict]:
    """Pull (jurisdiction, percent timely) pairs out of the APT HTML table.

    Looks for the data table whose header names a state column and a timely
    percentage column. Rows that are national totals or notes are skipped by
    the canonical lookup (try_normalize_code returns None for them).
    """
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict] = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            code = states.try_normalize_code(cells[0])
            if not code:
                continue
            value = _first_percent(cells[1:])
            if value is None:
                continue
            rows.append(
                {
                    "code": code,
                    "name": states.display_name(code),
                    "snap_apt_timely": value,
                }
            )
    return rows


def _first_percent(cells: list[str]):
    for raw in cells:
        cleaned = raw.replace("%", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            continue
    return None


def _parse_manual_csv(content: bytes) -> list[dict]:
    """Parse a simple two-column CSV (jurisdiction, percent timely)."""
    text = content.decode("utf-8-sig", errors="replace")
    rows: list[dict] = []
    reader = csv.reader(io.StringIO(text))
    for cells in reader:
        if len(cells) < 2:
            continue
        code = states.try_normalize_code(cells[0])
        if not code:
            continue
        value = _first_percent(cells[1:])
        if value is None:
            continue
        rows.append(
            {
                "code": code,
                "name": states.display_name(code),
                "snap_apt_timely": value,
            }
        )
    return rows


def _published_table_rows() -> list[dict]:
    """The published FY2024 APT table as transcribed in the project brief.

    Used as the source of record when the live FNS and FNA hosts are blocked
    by the execution environment. Provenance records this clearly; this is the
    published USDA FY2024 table (docs/LANDSCAPE_BRIEF.md Part B2), not a live
    scrape.
    """
    rows = []
    for name, value in anchors.SNAP_APT_FY2024.items():
        code = states.normalize_code(name)
        rows.append(
            {
                "code": code,
                "name": states.display_name(code),
                "snap_apt_timely": value,
            }
        )
    return rows


def _write_raw_csv(raw_dir: str, filename: str, rows: list[dict]) -> str:
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, filename)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["jurisdiction", "snap_apt_pct_timely"])
    for r in rows:
        writer.writerow([r["name"], r["snap_apt_timely"]])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    return path


def _write_raw_bytes(raw_dir: str, filename: str, content: bytes) -> str:
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, filename)
    with open(path, "wb") as fh:
        fh.write(content)
    return path


def fetch_snap_apt(fiscal_year: int = 2024, raw_dir: str = "data/raw") -> SourceFetch:
    """Fetch SNAP APT for a fiscal year. Tries fns then fna; logs the host.

    On a network-policy block, falls back to the published FY2024 table
    transcribed in the brief and records that the live fetch was blocked.
    """
    vintage = f"FY{fiscal_year}"
    candidates = _page_paths(fiscal_year)
    attempts: list[dict] = []

    # A user-provided SNAP APT file in data/raw/manual/ takes precedence over
    # both the live fetch and the brief-transcribed fallback, giving independent
    # verification against the anchors.
    manual_path = find_manual(
        raw_dir,
        [
            {"ext": ".html", "contains": ["apt"]},
            {"ext": ".html", "contains": ["snap"]},
            {"ext": ".html", "contains": ["timeliness"]},
            {"ext": ".csv", "contains": ["apt"]},
            {"ext": ".csv", "contains": ["snap"]},
        ],
    )
    if manual_path:
        with open(manual_path, "rb") as fh:
            content = fh.read()
        if manual_path.lower().endswith(".html"):
            rows = _parse_html_table(content, fiscal_year)
        else:
            rows = _parse_manual_csv(content)
        notes = [f"Parsed user-provided file: {os.path.basename(manual_path)}"]
        if not rows:
            notes.append("No rows parsed from the provided SNAP file.")
        return SourceFetch(
            source_id=SOURCE_ID,
            requested_vintage=vintage,
            vintage=vintage,
            rows=rows,
            provenance={
                "url": "manual",
                "host": "manual_upload",
                "status": None,
                "fetched_at": utc_now_iso(),
                "landing": LANDING,
                "raw_files": [manual_path],
                "live_fetch_blocked": False,
                "source_of_record": manual_path,
            },
            blocked=len(rows) == 0,
            notes=notes,
        )

    for url in candidates:
        try:
            result = fetch(url)
        except FetchBlocked as blocked:
            attempts.append(
                {
                    "url": blocked.url,
                    "host": blocked.host,
                    "status": None,
                    "blocked": True,
                    "deny_reason": blocked.deny_reason,
                }
            )
            continue

        attempts.append(
            {
                "url": result.url,
                "host": result.host,
                "status": result.status,
                "blocked": False,
                "deny_reason": result.deny_reason,
            }
        )
        if result.ok and result.content:
            raw_path = _write_raw_bytes(
                raw_dir, f"snap_apt_fy{fiscal_year % 100:02d}.html", result.content
            )
            rows = _parse_html_table(result.content, fiscal_year)
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
                    "raw_files": [raw_path],
                    "host_fallback_used": result.host.startswith("www.fna"),
                    "attempts": attempts,
                    "live_fetch_blocked": False,
                },
                notes=[f"served by {result.host}"],
            )

    # Every host was blocked or unreachable. Fall back to the published table.
    rows = _published_table_rows()
    raw_path = _write_raw_csv(
        raw_dir, f"snap_apt_fy{fiscal_year % 100:02d}_published.csv", rows
    )
    return SourceFetch(
        source_id=SOURCE_ID,
        requested_vintage=vintage,
        vintage=vintage,
        rows=rows,
        provenance={
            "url": candidates[0],
            "host": "blocked",
            "status": None,
            "fetched_at": utc_now_iso(),
            "landing": LANDING,
            "raw_files": [raw_path],
            "attempts": attempts,
            "live_fetch_blocked": True,
            "source_of_record": (
                "docs/LANDSCAPE_BRIEF.md Part B2: published USDA FNS SNAP APT "
                "FY2024 table, transcribed"
            ),
        },
        blocked=True,
        notes=[
            "Live FNS and FNA hosts blocked by environment network policy.",
            "Values taken from the published FY2024 table transcribed in the brief.",
        ],
    )


if __name__ == "__main__":
    out = fetch_snap_apt()
    print(f"snap_apt vintage={out.vintage} rows={len(out.rows)} blocked={out.blocked}")
    for note in out.notes:
        print("  note:", note)
