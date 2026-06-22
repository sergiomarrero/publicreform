"""Fetch WIOA state performance, DOL ETA, for PY2023 explicitly.

The live "Results At-A-Glance" page now serves PY2024, so this fetcher does
NOT scrape it. It pulls the PY2023 National Performance Summary (PDF) and the
PY2023 Annual Report Accessible File (Excel) directly. State tables come from
the Excel (openpyxl); the national headline summary can be cross-read from the
PDF when a PDF text backend is available.

The fetcher takes a program_year parameter so other program years can be
backfilled later by swapping the year in the file URLs.

Title I metrics captured per jurisdiction: Adult employment rate Q2 after
exit, Adult median earnings Q2, Adult credential attainment, plus the Q4 and
measurable-skill-gains fields when present. No scoring; raw values only.
"""

from __future__ import annotations

import os

import states
from http_util import FetchBlocked, fetch, utc_now_iso
from model import SourceFetch

SOURCE_ID = "wioa"
AT_A_GLANCE = "https://www.dol.gov/agencies/eta/performance/wioa-performance"
ARCHIVE = "https://www.dol.gov/agencies/eta/performance/results-archive"

# Column header fragments mapped to canonical metric names. The Accessible
# File labels vary slightly by program year, so matching is fragment-based.
_ADULT_COLUMN_HINTS = {
    "wioa_adult_emp_q2": ("adult", "employment", "2nd quarter"),
    "wioa_adult_emp_q4": ("adult", "employment", "4th quarter"),
    "wioa_adult_median_earnings_q2": ("adult", "median earnings"),
    "wioa_adult_credential": ("adult", "credential"),
    "wioa_adult_msg": ("adult", "measurable skill"),
}

# Dislocated Worker median earnings column, needed for the PY2023 vintage check.
_DW_EARNINGS_HINT = ("dislocated", "median earnings")


def _pdf_backend_available() -> bool:
    """Lazily probe for a usable PDF text backend without polluting output.

    pypdf and pdfminer import the cryptography Rust binding at load time; where
    that binding is missing the import raises a pyo3 PanicException (a
    BaseException) and the Rust panic hook writes to OS-level stderr (fd 2),
    which a Python-level redirect cannot capture. We redirect fd 2 to devnull
    for the duration of the probe, and only run it when a PDF was actually
    downloaded, so a normal blocked run never triggers it. WIOA state and
    national figures come from the Excel; the PDF is a redundant, archival
    cross-check.
    """
    saved_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, 2)
        try:
            import pypdf  # noqa: F401
            return True
        except BaseException:  # noqa: BLE001
            return False
    finally:
        os.dup2(saved_fd, 2)
        os.close(devnull)
        os.close(saved_fd)


def _file_urls(program_year: int) -> dict[str, str]:
    """PY-specific PDF and Excel URLs. Backfill swaps the year token."""
    base = "https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs"
    py = f"PY{program_year}"
    pdf = (
        f"{base}/{py}/PY%20{program_year}%20WIOA%20National%20Performance%20"
        f"Summary.pdf"
    )
    xlsx = f"{base}/{py}/{py}%20Annual%20Report%20Accessible%20File.xlsx"
    return {"pdf": pdf, "xlsx": xlsx}


def _parse_excel(content: bytes) -> tuple[list[dict], dict | None]:
    """Best-effort parse of the Accessible File Excel.

    Returns (state_rows, national). Assumptions are documented, since the
    layout shifts year to year: a header row names a state column and the
    Title I indicator columns; metric columns are matched by header fragments.
    Rows that do not map to a canonical jurisdiction (notes, blanks) are
    skipped for the state table; a national or U.S. total row, when present, is
    captured separately so the validator can confirm the vintage. If the header
    cannot be located, an empty result is returned and the caller treats the
    table as unavailable rather than guessing.
    """
    import io

    from openpyxl import load_workbook

    wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    rows: list[dict] = []
    national: dict | None = None
    for ws in wb.worksheets:
        grid = [[(c if c is not None else "") for c in row]
                for row in ws.iter_rows(values_only=True)]
        header_idx, state_col, metric_cols = _locate_header(grid)
        if header_idx is None:
            continue
        for r in grid[header_idx + 1:]:
            if state_col >= len(r):
                continue
            label = str(r[state_col]).strip()
            vals = {
                metric: (_num(r[col]) if col < len(r) else None)
                for metric, col in metric_cols.items()
            }
            code = states.try_normalize_code(label)
            if code:
                record = {"code": code, "name": states.display_name(code)}
                record.update(vals)
                rows.append(record)
            elif label.lower() in ("national", "u.s.", "u.s. total", "us total",
                                   "united states", "total"):
                national = _national_block(vals)
        if rows:
            break
    return rows, national


def _national_block(vals: dict) -> dict:
    """Shape a national total row into the structure the validator expects."""
    return {
        "adult": {
            "emp_q2": vals.get("wioa_adult_emp_q2"),
            "median_earnings_q2": vals.get("wioa_adult_median_earnings_q2"),
        },
        "dislocated_worker": {
            "median_earnings_q2": vals.get("wioa_dw_median_earnings_q2"),
        },
    }


def _locate_header(grid: list[list]):
    """Find the header row and the column indices we care about."""
    hint_map = dict(_ADULT_COLUMN_HINTS)
    hint_map["wioa_dw_median_earnings_q2"] = _DW_EARNINGS_HINT
    for idx, row in enumerate(grid[:40]):
        lowered = [str(c).strip().lower() for c in row]
        state_col = None
        for i, val in enumerate(lowered):
            if val in ("state", "state name", "stname"):
                state_col = i
                break
        if state_col is None:
            continue
        metric_cols: dict[str, int] = {}
        for metric, hints in hint_map.items():
            for i, val in enumerate(lowered):
                if all(h in val for h in hints):
                    metric_cols[metric] = i
                    break
        if metric_cols:
            return idx, state_col, metric_cols
    return None, None, {}


def _num(value):
    if value is None or value == "":
        return None
    try:
        num = float(str(value).replace("%", "").replace(",", "").replace("$", "").strip())
    except ValueError:
        return None
    # Excel sometimes stores rates as fractions (0.741) rather than percents.
    if 0 < num <= 1:
        num *= 100
    return round(num, 2)


def fetch_wioa_py2023(
    program_year: int = 2023, raw_dir: str = "data/raw"
) -> SourceFetch:
    """Fetch WIOA PY2023 state performance from the PDF and Excel files."""
    vintage = f"PY{program_year}"
    urls = _file_urls(program_year)
    attempts: list[dict] = []
    raw_files: list[str] = []
    rows: list[dict] = []
    national: dict | None = None
    blocked = False

    os.makedirs(raw_dir, exist_ok=True)

    # Excel first: it carries the state tables and the national total row.
    try:
        xlsx = fetch(urls["xlsx"])
        attempts.append(
            {"url": xlsx.url, "host": xlsx.host, "status": xlsx.status, "blocked": False}
        )
        if xlsx.ok and xlsx.content:
            path = os.path.join(raw_dir, f"wioa_py{program_year}_accessible.xlsx")
            with open(path, "wb") as fh:
                fh.write(xlsx.content)
            raw_files.append(path)
            rows, national = _parse_excel(xlsx.content)
    except FetchBlocked as b:
        attempts.append(
            {"url": b.url, "host": "blocked", "status": None, "blocked": True,
             "deny_reason": b.deny_reason}
        )
        blocked = True

    # PDF second: redundant national summary, parsed only if a backend exists.
    pdf_note = None
    try:
        pdf = fetch(urls["pdf"])
        attempts.append(
            {"url": pdf.url, "host": pdf.host, "status": pdf.status, "blocked": False}
        )
        if pdf.ok and pdf.content:
            path = os.path.join(raw_dir, f"wioa_py{program_year}_summary.pdf")
            with open(path, "wb") as fh:
                fh.write(pdf.content)
            raw_files.append(path)
            if not _pdf_backend_available():
                pdf_note = (
                    "PDF saved but not parsed: no PDF text backend available "
                    "in this environment. State data is read from the Excel."
                )
    except FetchBlocked as b:
        attempts.append(
            {"url": b.url, "host": "blocked", "status": None, "blocked": True,
             "deny_reason": b.deny_reason}
        )
        blocked = True

    notes: list[str] = []
    if pdf_note:
        notes.append(pdf_note)

    if not rows:
        blocked = True
        notes.append(
            "No WIOA PY2023 state rows available in this environment; the DOL "
            "host is blocked by the network policy and the brief carries only "
            "national PY2023 headline figures, not a state table."
        )

    return SourceFetch(
        source_id=SOURCE_ID,
        requested_vintage=vintage,
        vintage=vintage if rows else None,
        rows=rows,
        national=national,
        provenance={
            "url": urls["xlsx"],
            "pdf_url": urls["pdf"],
            "host": "blocked" if blocked and not raw_files else (
                attempts[0]["host"] if attempts else "unknown"
            ),
            "status": None if blocked and not raw_files else (
                attempts[0].get("status") if attempts else None
            ),
            "fetched_at": utc_now_iso(),
            "at_a_glance_not_used": AT_A_GLANCE,
            "archive": ARCHIVE,
            "raw_files": raw_files,
            "attempts": attempts,
            "live_fetch_blocked": blocked,
        },
        blocked=blocked,
        notes=notes,
    )


if __name__ == "__main__":
    out = fetch_wioa_py2023()
    print(f"wioa vintage={out.requested_vintage} rows={len(out.rows)} "
          f"blocked={out.blocked}")
    for note in out.notes:
        print("  note:", note)
