# BUILD SPEC: Public Reform State Dashboard (v1)

This is the instruction set Claude Code executes. Background and source detail live in `docs/LANDSCAPE_BRIEF.md`. Read that first, then build to this spec.

## What we are building

A public-facing, state-level **data dashboard** characterizing how US public-benefit and workforce systems perform across three dimensions: **speed**, **fragmentation**, and **navigability**, anchored on three programs: Unemployment Insurance (UI), SNAP, and WIOA.

**v1 leads with the raw-data dashboard, not scores.** Each state shows its actual metrics side by side, sortable. A blended 0-100 composite index is explicitly deferred to a later stage and must NOT block v1.

Primary audience: a foundation research team (defensible rigor, every figure sourced and vintage-stamped). Secondary: a general LinkedIn/brand audience (readable in three minutes).

## Hard constraints

- **Scope:** 50 states + DC for any ranked/compared view. Territories (PR, Guam, USVI) shown where data exists but flagged and excluded from any cross-state ranking.
- **Stack:** Static React front end, static JSON data layer, no backend. Deploy to Vercel. Do NOT add Supabase or any database in v1.
- **No silent numbers.** Every metric rendered in the UI carries a source label and a vintage (e.g., "SNAP APT, FY2024, USDA FNS"). A figure with no provenance does not ship.
- **Verify before render.** The pipeline validates scraped values against the known-good anchors in this spec before writing the JSON the UI consumes. A failed check stops the build with a clear error; it does not silently publish.
- **Descriptive and correlational only.** No causal language anywhere in copy. The dashboard highlights variation; it does not claim administration causes mobility outcomes.
- **Style:** no em dashes anywhere in code comments, UI copy, or docs (use commas, semicolons, colons, or parentheses). Use "economic mobility" not "poverty." Concise and direct.

## Stage 1: Data pipeline (build and verify FIRST)

Write the pipeline in Python under `pipeline/`. Each source gets its own fetcher module plus a shared normalize/validate step. Output is versioned JSON under `data/` that the React app imports.

**Sources to ingest in v1 (single most-recent vintage each):**

1. **UI first-payment timeliness, DOL ETA 9050.** SPEED.
   - Source: https://oui.doleta.gov/unemploy/DataDownloads.asp (ETA 9050, comma-delimited CSV). Report-builder reference: https://oui.doleta.gov/unemploy/btq.asp
   - Pull the latest available month. Key metric: % of intrastate first payments within 14/21 days. Federal Secretary's Standard = 87% within 14/21 days (flag states below it).
   - Format is CSV, so this is a download-and-parse, not a scrape.

2. **SNAP Application Processing Timeliness (APT), USDA FNS.** SPEED.
   - Source: https://www.fns.usda.gov/snap/qc/timeliness/apt-fy24 (FY2024, posted March 17, 2026). Landing: https://www.fns.usda.gov/snap/qc/timeliness
   - HTML table, so scrape to file. Key metric: % of applications processed timely (30-day regular / 7-day expedited). Corrective-action threshold = 90% (flag states below it).

3. **WIOA state performance, DOL ETA.** SPEED-of-employment + outcome.
   - Pull **PY2023** explicitly. The live At-A-Glance page (https://www.dol.gov/agencies/eta/performance/wioa-performance) now serves PY2024, so DO NOT scrape the live page for PY2023. Use the PY2023 National Performance Summary PDF (https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs/PY2023/PY%202023%20WIOA%20National%20Performance%20Summary.pdf) and the PY2023 Annual Report Accessible File Excel (https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs/PY2023/PY2023%20Annual%20Report%20Accessible%20File.xlsx) for state tables.
   - Key metrics: Title I Adult and Dislocated Worker, employment rate Q2 after exit, employment rate Q4 after exit, median earnings Q2, credential attainment, measurable skill gains.

**Normalization rules:**
- Standardize every state to a two-letter code; keep a single canonical state lookup.
- Store raw values with their units; do not pre-blend or pre-score anything in v1.
- Direction is consistent across the three speed metrics (higher = better), but do not compute a speed sub-score yet; just land the raw fields.
- Territories tagged with an `excluded_from_ranking: true` flag.
- Missing values are explicit nulls with a reason field; never impute silently.

**Validation gate (must pass before JSON is written for the UI):**
- SNAP APT FY2024: assert the scraped values match the anchor table in `docs/LANDSCAPE_BRIEF.md` (Part B2) within a small tolerance. Spot anchors: Wisconsin 95.62 (max), Tennessee 42.72 (min), DC 56.73, California 80.21. If the top/bottom or these spot states do not match, fail loudly.
- WIOA PY2023: assert national Adult Q2 employment ≈ 74.1% and Dislocated Worker median earnings ≈ $9,397 (the PY2023 anchors). If the numbers instead match the PY2024 reference set in the brief, fail with "WIOA vintage mismatch: looks like PY2024, expected PY2023."
- UI ETA 9050: assert all 50 states + DC are present and the within-14/21-day metric is between 0 and 100.
- Emit a `data/validation_report.json` summarizing pass/fail per source and the vintage actually ingested.

**URL-migration guard:** before fetching SNAP, check both `fns.usda.gov` and `fna.usda.gov` (FNS renamed to the Food and Nutrition Administration on June 1, 2026). If the fns.usda.gov path 404s, retry the fna.usda.gov equivalent and log which host served the data.

## Stage 2: Dashboard UI (build only after Stage 1 validates)

- Single-page React app under `app/` (or the framework you prefer that deploys cleanly to Vercel as static). Imports the validated JSON from `data/`.
- Default view: a **sortable table**, one row per state, columns grouped by dimension. v1 columns: UI % within 14/21 days; SNAP APT % timely; WIOA Adult Q2 employment %; WIOA Adult median earnings; WIOA credential %. Each column header carries a tooltip with the metric definition, source, and vintage.
- Visual flags: states below the SNAP 90% corrective-action threshold and below the UI 87% standard render with a clear "below federal standard" marker.
- Sort on any column; default sort alphabetical by state. Include a simple search/filter by state name.
- A "Sources and vintages" panel or footer listing every dataset, its agency, its vintage, and a link to the primary source. This is non-negotiable for the foundation audience.
- A short, plain-language methodology note: what each dimension means, that v1 shows raw data only, and that the data is descriptive and correlational. No causal claims.
- Keep the composite-index toggle as a visibly "coming soon" placeholder so the structure is there but no score is computed or shown.

## Stage 3 (DEFERRED, do not build in v1)

Composite 0-100 index: percentile-rank normalization, equal weighting within and across speed/fragmentation/navigability, published ±20% weight sensitivity analysis, EIG-style quintile tiers. Fragmentation and navigability sub-scores require the Code for America integrated-application counts, Beeck DBN flags, and hand-coded intake-system counts described in the brief. Leave a clean extension point; build nothing scored yet.

## Repo layout

```
publicreform/
  README.md                  (project overview, how to run pipeline + app)
  docs/
    LANDSCAPE_BRIEF.md        (background, already provided)
    BUILD_SPEC.md             (this file)
  pipeline/
    fetch_ui_eta9050.py
    fetch_snap_apt.py
    fetch_wioa_py2023.py
    normalize.py
    validate.py
    run_all.py                (orchestrates fetch -> normalize -> validate -> write data/)
  data/
    states.json               (the validated output the UI consumes)
    validation_report.json
    raw/                       (downloaded source files, see archive note below)
  app/                         (React dashboard)
  archive/
    MANIFEST.md                (what gets backed up to Glacier, already provided)
    glacier_archive.sh         (generated; user runs it locally)
```

## Backup hook (see archive/MANIFEST.md)

As the pipeline downloads source files, write them to `data/raw/` with their original filenames and a `data/raw/SOURCES.json` recording URL, host served, fetch timestamp, and vintage for each. The Glacier archive step (run separately by the user) reads that folder. Code and cleaned data stay in GitHub as normal; only the primary research files go to Glacier per the manifest rule: archive the complete file wherever the full file was downloaded, archive a citation pointer where only a partial or paywalled source was reachable.

## Definition of done for v1

1. `python pipeline/run_all.py` fetches all three sources, validates against the anchors, and writes `data/states.json` plus `data/validation_report.json` with every check passing.
2. The React app renders the sortable state table from `data/states.json`, with source/vintage labels, federal-standard flags, a sources panel, and the methodology note.
3. Deploys to Vercel as a static site with no backend.
4. `data/raw/` holds the downloaded primary files and `SOURCES.json`; `archive/glacier_archive.sh` and `archive/MANIFEST.md` are present for the user to run the backup.
5. No em dashes, no causal claims, no unsourced numbers anywhere.
