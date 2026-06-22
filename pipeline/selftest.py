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
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append([
        "State",
        "Adult Employment Rate 2nd Quarter After Exit",
        "Adult Employment Rate 4th Quarter After Exit",
        "Adult Median Earnings 2nd Quarter After Exit",
        "Adult Credential Attainment Rate",
        "Adult Measurable Skill Gains",
        "Dislocated Worker Median Earnings 2nd Quarter After Exit",
    ])
    ws.append(["California", 0.731, 0.725, 8500, 0.70, 0.69, 9200])
    ws.append(["Texas", 75.2, 74.1, 8900, 71.5, 70.0, 9500])
    ws.append(["National", 74.1, 73.4, 8677, 72.2, 71.2, 9397])
    buf = io.BytesIO()
    wb.save(buf)

    rows, national = fetch_wioa_py2023._parse_excel(buf.getvalue())
    by_code = {r["code"]: r for r in rows}
    ok = True
    ok &= _check("wioa state rows parsed", len(rows) == 2, f"{len(rows)} rows")
    ok &= _check("wioa fraction normalized to percent",
                 by_code.get("CA", {}).get("wioa_adult_emp_q2") == 73.1)
    ok &= _check("wioa percent left as-is",
                 by_code.get("TX", {}).get("wioa_adult_emp_q2") == 75.2)
    ok &= _check("wioa earnings parsed",
                 by_code.get("CA", {}).get("wioa_adult_median_earnings_q2") == 8500)
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
