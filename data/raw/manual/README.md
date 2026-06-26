# Manual-fetch drop folder

Download the primary source files and drop them here. The pipeline checks this
folder first, so when a file is present the fetchers use it instead of the live
host, and no network access is needed. Matching is by file extension plus tokens
in the name, so the original download names generally work without renaming.

## Files to add for the two pending dimensions

### UI: DOL ETA 9050 first-payment time lapse
- Get it from: https://oui.doleta.gov/unemploy/DataDownloads.asp (ETA 9050,
  comma-delimited CSV). Report builder, if you need the computed percentage:
  https://oui.doleta.gov/unemploy/btq.asp
- Save as a `.csv` whose name contains `9050` (for example `eta9050.csv`).
- The parser looks for a state column and a within-14/21-day percentage column.
  If the raw file has only time-lapse counts and no computed percentage, say so
  and the parser will be adjusted to read the right export.

### WIOA: DOL PY2023 state performance
- Get it from:
  https://www.dol.gov/sites/dolgov/files/ETA/Performance/pdfs/PY2023/PY2023%20Annual%20Report%20Accessible%20File.xlsx
- Save the `.xlsx` with a name containing `Accessible` or `WIOA` or `PY2023`
  (the default download name already works).
- Optional companion PDF (National Performance Summary) can be added too; it is
  archived but the state tables are read from the Excel.

### SNAP (optional, for independent verification)
- FY2024 SNAP APT is already populated from the published table in the brief.
- To verify it against the live page instead, save the table as `.html` or
  `.csv` with a name containing `apt` or `snap`. A provided file takes
  precedence over the brief-transcribed values.

## After adding files

Re-run the pipeline:

```
python pipeline/run_all.py
python pipeline/build_app_data.py
```

When the validation gate passes, `data/states.json` is written and the full
dashboard build is ready to commit and deploy. Only primary research files
belong here; cleaned or derived data does not.
