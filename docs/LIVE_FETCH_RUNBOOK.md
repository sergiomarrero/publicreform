# Live fetch runbook: fill all five dimensions

This is for a session that has outbound network access to the source hosts. It
takes the dashboard from the interim SNAP-only build to the full five-dimension
build. Follow it top to bottom.

## Prerequisite: network access

The session's network policy must allow these hosts:

- `oui.doleta.gov` (UI ETA 9050)
- `fns.usda.gov` and `fna.usda.gov` (SNAP APT)
- `www.dol.gov` (WIOA PY2023 PDF and Excel)

Quick check:

```
curl -s -o /dev/null -w "%{http_code}\n" https://www.dol.gov/agencies/eta/performance/wioa-performance
```

A 200 (or a normal redirect) means reachable. A 403 with `x-deny-reason: host_not_allowed` means the policy still blocks it; stop and widen the policy first.

## Steps

```
# 1. Dependencies
pip install -r pipeline/requirements.txt
npm --prefix app install

# 2. Live fetch, normalize, validate, write data/states.json
python pipeline/run_all.py

# 3. Regenerate the app dataset from the validated output
python pipeline/build_app_data.py

# 4. Ship: commit data and app dataset, push to main (production)
git add data app/src/data
git commit -m "Live data: full five-dimension build (UI, SNAP, WIOA PY2023)"
git push origin HEAD:main
```

Vercel auto-redeploys `main` to production. Confirm at https://publicreform.vercel.app .

## What a clean run looks like

`data/validation_report.json` should report `"overall_pass": true`, with:

- SNAP APT FY2024 spot anchors matched: Wisconsin 95.62 (max), Tennessee 42.72
  (min), DC 56.73, California 80.21. Once fetched live, `verification_mode`
  becomes `independent_source` rather than `transcription_consistency`.
- WIOA vintage confirmed as PY2023: national Adult Q2 employment near 74.1
  percent and Dislocated Worker median earnings near $9,397. If it instead
  matches PY2024 (Adult Q2 72.2, DW median $9,897), the gate fails with a
  vintage mismatch; that means a wrong file was pulled.
- All 51 ranking jurisdictions present with a UI value between 0 and 100.

When the gate passes, `build_app_data.py` stamps the dataset `status: full`, the
interim banner disappears, and all five columns render.

## If a parser needs a small adjustment

The fetchers match columns by header fragments, so a live file whose headers
differ slightly may need a one-line tweak. The places to look:

- UI ETA 9050: `pipeline/fetch_ui_eta9050.py`, `_PCT_NORM_SIGNATURES` and
  `_find_pct_idx` (the within-14/21-day percentage column), and
  `RAW_CSV_CANDIDATES` (the raw file URL). Run `python pipeline/selftest.py` to
  confirm the parser still passes after any change.
- WIOA: `pipeline/fetch_wioa_py2023.py`, `_ADULT_COLUMN_HINTS`,
  `_DW_EARNINGS_HINT`, and `_locate_header` (state and indicator columns in the
  Accessible File Excel).
- SNAP: `pipeline/fetch_snap_apt.py`, `_parse_html_table`. When the live FNS or
  FNA host serves the table, this replaces the brief-transcribed fallback.

Each fetcher takes a date or vintage parameter, so other vintages backfill by
changing the argument (for example `fetch_snap_apt(fiscal_year=2023)`).

## Project facts

- Vercel project: `publicreform`, production branch `main`, static build from
  `vercel.json` (output `app/dist`). No backend, no environment variables.
- Constraints still apply: no em dashes, no causal language, every rendered
  number carries a source and vintage, ranked views scope to 50 states and DC.
