"""Locate user-provided source files in data/raw/manual/.

When the live hosts are unreachable, the primary files can be downloaded by
hand and dropped into data/raw/manual/. The fetchers check here first, so the
pipeline can run entirely from those files with no network access. Matching is
case-insensitive on the file extension plus a set of required filename tokens,
so the original download names generally work without renaming.
"""

from __future__ import annotations

import os


def find_manual(raw_dir: str, specs: list[dict]) -> str | None:
    """Return the first file in data/raw/manual/ matching any spec.

    Each spec is {"ext": ".csv", "contains": ["9050"]}: the filename must end
    with ext (when given) and contain every token in contains (case-insensitive).
    Specs are tried in order; within a spec, files are tried alphabetically.
    """
    manual_dir = os.path.join(raw_dir, "manual")
    if not os.path.isdir(manual_dir):
        return None
    files = sorted(
        f
        for f in os.listdir(manual_dir)
        if os.path.isfile(os.path.join(manual_dir, f))
    )
    for spec in specs:
        ext = spec.get("ext", "")
        tokens = [t.lower() for t in spec.get("contains", [])]
        for f in files:
            fl = f.lower()
            if ext and not fl.endswith(ext):
                continue
            if all(t in fl for t in tokens):
                return os.path.join(manual_dir, f)
    return None
