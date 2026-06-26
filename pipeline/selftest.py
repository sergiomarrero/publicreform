"""Offline self-test for the parsers.

The live source hosts may be unreachable in a given environment, so this test
proves the parse logic against realistic fixtures shaped like the real files:
a SNAP HTML table, an ETA 9050 CSV with a precomputed within-14/21-day column,
and a WIOA Accessible File Excel with state rows plus a national total row.

These fixtures confirm the parsers extract the right fields and map labels to
canonical codes. They do not confirm the exact live schema; the first reachable
run pins any column-name differences against the real files.

Run: python pipeline/selftest.py
"""

from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_snap_apt  # noqa: E402
import fetch_ui_eta9050  # noqa: E402
import fetch_wioa_py2023  # noqa: E402


def _check(name: str, condition: bool, detail: str = "") -> bool:
    status = "pass" if condition else "FAIL"
    print(f"  [{status}] {name}{(': ' + detail) if detail else ''}")
    return condition


def test_snap_html() -> bool:
    html = b"""
    <html><body>
    <table>
      <tr><th>State</th><th>Percent Timely</th></tr>
      <tr><td>Wisconsin</td><td>95.62%</td></tr>
      <tr><td>California</td><td>80.21</td></tr>
      <tr><td>Tennessee</td><td>42.72</td></tr>
      <tr><td>U.S. Virgin Islands</td><td>77.63</td></tr>
      <tr><td>United States</td><td>83.10</td></tr>
    </table>
    </body></html>
    """
    rows = fetch_snap_apt._parse_html_table(html, 2024)
    by_code = {r["code"]: r["snap_apt_timely"] for r in rows}
    ok = True
    ok &= _check("snap rows parsed", len(rows) == 4, f"{len(rows)} rows (US total skipped)")
    ok &= _check("snap WI value", by_code.get("WI") == 95.62)
    ok &= _check("snap CA value", by_code.get("CA") == 80.21)
    ok &= _check("snap territory mapped", by_code.get("VI") == 77.63)
    return ok


def test_ui_csv_precomputed() -> bool:
    csv_text = (
        "st,rptdate,pct_within_1421,first_payments\n"
        "CA,2026-05-01,88.4,12000\n"
        "TX,2026-05-01,79.9,9000\n"
        "NY,2026-05-01,91.2,8000\n"
    )
    rows, notes = fetch_ui_eta9050._parse_csv(csv_text.encode("utf-8"), 2026, 5)
    by_code = {r["code"]: r["ui_first_pay_14_21"] for r in rows}
    ok = True
    ok &= _check("ui rows parsed", len(rows) == 3, f"{len(rows)} rows")
    ok &= _check("ui CA value", by_code.get("CA") == 88.4)
    ok &= _check("ui range respected", all(0 <= v <= 100 for v in by_code.values()))
    return ok


def test_wioa_excel() -> bool:
    # Mirror the real Accessible File: a Performance sheet, one row per
    # (state, program), separate Target and Actual columns, a National US row.
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Performance"
    ws.append([
        "State Name", "State Code", "Program",
        "Total Statewide: Total Participants Served",
        "Total Statewide: Total Participants Exited",
        "Total Statewide, Target: Employment Q2 Rate",
        "Total Statewide, Target: Employment Q4 Rate",
        "Total Statewide, Target: Median Earnings",
        "Total Statewide, Target: Credential Rate",
        "Total Statewide, Target: Measurable Skills Rate",
        "Total Statewide, Actual: Employment Q2 Number",
        "Total Statewide, Actual: Employment Q2 Rate",
        "Total Statewide, Actual: Employment Q4 Number",
        "Total Statewide, Actual: Employment Q4 Rate",
        "Total Statewide, Actual: Median Earnings",
        "Total Statewide, Actual: Credential Number",
        "Total Statewide, Actual: Credential Rate",
        "Total Statewide, Actual: Measurable Skills Number",
        "Total Statewide, Actual: Measurable Skills Rate",
    ])
    # row: ..., actual emp_q2 rate at index 11, median at 14, credential at 16.
    def row(name, code, program, q2, median, cred):
        return [name, code, program, 100, 80, "N/A", "N/A", "N/A", "N/A", "N/A",
                70, q2, 70, 0.72, median, 50, cred, 60, 0.70]

    ws.append(row("National", "US", "WIOA Adult", 0.741, 8677, 0.722))
    ws.append(row("National", "US", "WIOA Dislocated Worker", 0.707, 9397, 0.735))
    ws.append(row("California", "CA", "WIOA Adult", 0.684, 8640, 0.688))
    ws.append(row("Texas", "TX", "WIOA Adult", 0.752, 8900, 0.715))
    ws.append(row("California", "CA", "WIOA Youth", 0.50, 5000, 0.50))  # ignored
    buf = io.BytesIO()
    wb.save(buf)

    rows, national = fetch_wioa_py2023._parse_excel(buf.getvalue())
    by_code = {r["code"]: r for r in rows}
    ok = True
    ok &= _check("wioa adult state rows parsed", len(rows) == 2, f"{len(rows)} rows")
    ok &= _check("wioa fraction normalized to percent",
                 by_code.get("CA", {}).get("wioa_adult_emp_q2") == 68.4)
    ok &= _check("wioa earnings parsed",
                 by_code.get("CA", {}).get("wioa_adult_median_earnings_q2") == 8640)
    ok &= _check("wioa national captured", national is not None)
    if national:
        ok &= _check("wioa national adult Q2 = 74.1",
                     national["adult"]["emp_q2"] == 74.1)
        ok &= _check("wioa national DW earnings = 9397",
                     national["dislocated_worker"]["median_earnings_q2"] == 9397)
    return ok


def main() -> int:
    print("Parser self-test (offline fixtures):\n")
    results = []
    print("SNAP HTML table:")
    results.append(test_snap_html())
    print("\nUI ETA 9050 CSV (precomputed percent):")
    results.append(test_ui_csv_precomputed())
    print("\nWIOA Accessible File Excel:")
    results.append(test_wioa_excel())
    passed = all(results)
    print(f"\nself-test: {'ALL PASS' if passed else 'FAILURES PRESENT'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
