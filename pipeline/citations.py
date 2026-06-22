"""Write citation-pointer stubs for sources that are not freely downloadable.

The archive manifest rule: archive the complete file wherever the pipeline
downloaded it (Tier 1), and archive a small citation pointer where only a
partial, abstract, or paywalled source was reachable (Tier 2). A clean pointer
beats a half-saved report.

These stubs land in data/raw/citations/ so the Glacier archive step captures
them alongside the Tier 1 raw files. Each stub records title, author, URL,
vintage, and an access note. No scraped fragments.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

# Tier 2 and manual-fetch items from archive/MANIFEST.md. Full files are not
# freely downloadable, so a pointer is archived instead of a partial capture.
CITATION_POINTERS = [
    {
        "id": "herd_moynihan_administrative_burden",
        "title": "Administrative Burden: Policymaking by Other Means",
        "author": "Pamela Herd and Donald Moynihan",
        "publisher": "Russell Sage Foundation",
        "url": "https://www.russellsage.org/publications/book/administrative-burden",
        "vintage": "2018",
        "tier": 2,
        "access_note": "Book, not a free full-text file. Pointer only.",
    },
    {
        "id": "eig_dci_zip_county_dataset",
        "title": "EIG Distressed Communities Index, ZIP and county dataset",
        "author": "Economic Innovation Group",
        "url": "https://eig.org/dci-hub/",
        "vintage": "2025",
        "tier": 2,
        "access_note": (
            "Free but behind a license tied to a .org/.edu/.gov email. Manual "
            "fetch by the user; promote to a full-file archive once downloaded "
            "into data/raw/manual/."
        ),
    },
    {
        "id": "code_for_america_benefits_enrollment_field_guide",
        "title": "Benefits Enrollment Field Guide",
        "author": "Code for America",
        "url": "https://codeforamerica.org/explore/benefits-enrollment-field-guide/",
        "vintage": "2023 (incremental update noted September 2025)",
        "tier": 2,
        "access_note": "Interactive site, not a single file. Capture summary and URL.",
    },
    {
        "id": "annals_aapss_fewer_burdens_greater_inequality",
        "title": "Fewer Burdens but Greater Inequality?",
        "author": "ANNALS of the AAPSS",
        "url": "https://doi.org/10.1177/00027162231198976",
        "vintage": "2023",
        "tier": 2,
        "access_note": "Paywalled journal article. Pointer unless an open PDF exists.",
    },
]


def write_citation_pointers(raw_dir: str = "data/raw") -> list[str]:
    """Write one JSON stub per Tier 2 / manual item. Returns the paths."""
    out_dir = os.path.join(raw_dir, "citations")
    os.makedirs(out_dir, exist_ok=True)
    written: list[str] = []
    stamp = datetime.now(timezone.utc).isoformat()
    for item in CITATION_POINTERS:
        record = dict(item)
        record["citation_pointer"] = True
        record["written_at"] = stamp
        path = os.path.join(out_dir, f"{item['id']}.citation.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2)
        written.append(path)
    return written


if __name__ == "__main__":
    for p in write_citation_pointers():
        print("wrote", p)
