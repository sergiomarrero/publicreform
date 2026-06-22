"""Shared data structures passed between fetchers, the normalizer, and the
validator. Keeping these in one place keeps provenance consistent across the
three sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceFetch:
    """Normalized result of fetching one source at one vintage.

    rows: one dict per jurisdiction, keyed by canonical metric names plus a
          two-letter code and display name. Raw values, no scoring.
    national: optional national headline block (WIOA uses it for the
          vintage check; the others leave it None).
    provenance: everything SOURCES.json needs (url, host served, status,
          timestamp, vintage, blocked flag, deny reason, saved raw files).
    """

    source_id: str
    requested_vintage: str
    vintage: str | None
    rows: list[dict] = field(default_factory=list)
    national: dict | None = None
    provenance: dict = field(default_factory=dict)
    blocked: bool = False
    notes: list[str] = field(default_factory=list)

    def by_code(self) -> dict[str, dict]:
        return {r["code"]: r for r in self.rows if r.get("code")}

    def to_sources_entry(self) -> dict[str, Any]:
        """Compact provenance record for data/raw/SOURCES.json."""
        entry = dict(self.provenance)
        entry.setdefault("source_id", self.source_id)
        entry.setdefault("requested_vintage", self.requested_vintage)
        entry.setdefault("vintage", self.vintage)
        entry.setdefault("blocked", self.blocked)
        if self.notes:
            entry.setdefault("notes", self.notes)
        return entry
