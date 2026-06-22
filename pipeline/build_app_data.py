"""Produce the dataset the React app imports.

Prefers data/states.json (written only when the validation gate passes). When
that file is absent because the gate has not passed yet, it falls back to
data/states.preview.json and stamps the dataset as an interim build so the UI
can show clearly which dimensions are live and which are pending a source.

Run: python pipeline/build_app_data.py
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone

DATA_DIR = "data"
APP_DATA_DIR = os.path.join("app", "src", "data")
APP_DATA_PATH = os.path.join(APP_DATA_DIR, "states.json")


def _metric_complete(dataset: dict, key: str) -> bool:
    return dataset["metrics"].get(key, {}).get("available", False)


def main() -> int:
    full = os.path.join(DATA_DIR, "states.json")
    preview = os.path.join(DATA_DIR, "states.preview.json")
    if os.path.exists(full):
        src, status = full, "full"
    elif os.path.exists(preview):
        src, status = preview, "interim"
    else:
        raise SystemExit(
            "No dataset found. Run python pipeline/run_all.py first."
        )

    with open(src, encoding="utf-8") as fh:
        dataset = json.load(fh)

    live = [k for k in dataset["metrics"] if _metric_complete(dataset, k)]
    pending = [k for k in dataset["metrics"] if not _metric_complete(dataset, k)]

    dataset["meta"]["build"] = {
        "status": status,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_file": os.path.basename(src),
        "live_metrics": live,
        "pending_metrics": pending,
        "note": (
            "Full build: every dimension validated against its anchor."
            if status == "full"
            else (
                "Interim build. Live dimensions are validated and labeled with "
                "source and vintage. Pending dimensions are shown as pending a "
                "source, not as numbers, until their live feed is ingested."
            )
        ),
    }

    os.makedirs(APP_DATA_DIR, exist_ok=True)
    with open(APP_DATA_PATH, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=2)
    print(f"wrote {APP_DATA_PATH} from {src} (status={status})")
    print(f"  live metrics:    {live}")
    print(f"  pending metrics: {pending}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
