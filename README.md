# Public Reform State Dashboard

A public-facing, state-level data dashboard characterizing how US public-benefit
and workforce systems perform across speed, fragmentation, and navigability,
anchored on three programs: Unemployment Insurance (UI), SNAP, and WIOA.

v1 leads with the raw-data dashboard, not scores. Each state shows its actual
metrics side by side, sortable, with a source and vintage label on every figure.
A blended 0 to 100 composite index is deferred to a later stage.

Authoritative instructions live in `docs/BUILD_SPEC.md`. Background and the
source catalog live in `docs/LANDSCAPE_BRIEF.md`.

## Status

- Stage 1 (data pipeline + validation gate): built. See below.
- Stage 2 (React dashboard): not started, gated on a clean Stage 1 validation.
- Stage 3 (composite 0 to 100 index): deferred by design.

## Stage 1: data pipeline

The pipeline fetches three sources at their most recent single vintage,
normalizes to 50 states plus DC (territories shown but flagged and excluded from
ranking), validates against known-good anchors, and only then writes the JSON
the UI consumes.

| Source | Program | Vintage | Format | Key metric |
|--------|---------|---------|--------|------------|
| DOL ETA 9050 | UI | latest month | CSV download | percent of first payments within 14/21 days |
| USDA FNS SNAP APT | SNAP | FY2024 | scraped HTML | percent of applications processed timely |
| DOL WIOA State Performance | WIOA | PY2023 | PDF + Excel | Adult Q2 employment, median earnings, credential |

Run it:

```
pip install -r pipeline/requirements.txt
python pipeline/run_all.py
```

Outputs:

- `data/raw/` plus `data/raw/SOURCES.json`: downloaded source files and full
  provenance (URL, host served, timestamp, vintage, whether the live host was
  blocked).
- `data/validation_report.json`: pass, fail, or blocked per check, and the
  vintage actually ingested.
- `data/states.json`: the validated dataset the UI imports. Written only when
  every validation check passes. If the gate does not pass, the pipeline writes
  `data/states.preview.json` for inspection instead and does not publish.

### Validation gate

Before any UI-facing JSON is written, the gate asserts:

- SNAP APT FY2024 matches the published anchor table, including the spot states
  Wisconsin 95.62 (max), Tennessee 42.72 (min), DC 56.73, and California 80.21.
- WIOA national Adult Q2 employment is about 74.1 percent and Dislocated Worker
  median earnings about $9,397, the PY2023 anchors. If the figures instead match
  the PY2024 reference set, the gate fails with a vintage mismatch error.
- All 51 ranking jurisdictions are present with a UI value within 0 to 100.

A failed or blocked check stops the build. The pipeline never silently
publishes unverified numbers.

### URL-migration and vintage guards

- SNAP: the fetcher tries `fns.usda.gov` first, then `fna.usda.gov` (the agency
  was renamed to the Food and Nutrition Administration on June 1, 2026), and
  logs which host served the data.
- WIOA: the fetcher pulls the PY2023 PDF and Excel directly and does NOT scrape
  the live At-A-Glance page, which now serves PY2024.
- Every scraper takes a date or vintage parameter so earlier vintages can be
  backfilled later without a rewrite.

### Network access note

The three primary hosts (`oui.doleta.gov`, `fns.usda.gov` / `fna.usda.gov`, and
`www.dol.gov`) must be reachable for a live fetch. In a restricted environment
that allowlists only specific hosts, the live fetch is blocked and the pipeline
records this in `SOURCES.json` and the validation report rather than failing
silently. To run a clean live fetch, run the pipeline where those hosts are
reachable, or drop the downloaded source files into `data/raw/manual/` and point
the fetchers at them.

## Backup hook (AWS Glacier)

`archive/glacier_archive.sh` reads `data/raw/` and `data/raw/manual/`, builds a
timestamped tar plus a sha256 checksum manifest, prints the exact upload
command, and writes `archive/last_backup.json`. It contains no credentials and
does not upload; you review the file list and run the upload yourself. See
`archive/MANIFEST.md` for what gets archived and the Tier 1 / Tier 2 rule.

## Repo layout

```
publicreform/
  README.md
  docs/            BUILD_SPEC.md, LANDSCAPE_BRIEF.md
  pipeline/        fetchers, normalize, validate, run_all, anchors, states
  data/            states.json (when the gate passes), validation_report.json, raw/
  app/             React dashboard (Stage 2, not started)
  archive/         MANIFEST.md, glacier_archive.sh
```

## Constraints carried throughout

- Scope any ranked view to 50 states plus DC; territories are flagged and
  excluded from ranking.
- Every rendered number carries a source and a vintage label.
- The data is descriptive and correlational; no causal language anywhere.
- No em dashes in code, copy, or comments.
