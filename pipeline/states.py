"""Canonical jurisdiction lookup for the Public Reform state dashboard.

One source of truth for jurisdiction names, two-letter codes, and ranking
scope. Ranked or compared views cover 50 states plus DC (51 jurisdictions).
Territories are kept where data exists but flagged excluded_from_ranking so
they never enter a cross-state comparison.

No causal language, no em dashes anywhere in this project.
"""

from __future__ import annotations

# 50 states plus DC. These are the only jurisdictions eligible for ranking.
RANKING_JURISDICTIONS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

# Territories: shown where data exists, never ranked against the 51.
TERRITORIES = {
    "PR": "Puerto Rico",
    "GU": "Guam",
    "VI": "U.S. Virgin Islands",
}

# Full canonical set (code -> canonical display name).
CANONICAL = {**RANKING_JURISDICTIONS, **TERRITORIES}

# Alternate spellings and abbreviations seen across DOL and USDA tables,
# normalized to the canonical two-letter code. Keys are lowercased.
_ALIASES = {
    "district of columbia": "DC",
    "d.c.": "DC",
    "dc": "DC",
    "washington dc": "DC",
    "washington d.c.": "DC",
    "puerto rico": "PR",
    "pr": "PR",
    "guam": "GU",
    "gu": "GU",
    "u.s. virgin islands": "VI",
    "us virgin islands": "VI",
    "u.s.virgin islands": "VI",
    "virgin islands": "VI",
    "virgin islands of the u.s.": "VI",
    "vi": "VI",
}

# Build the name -> code lookup once. Includes canonical names, the codes
# themselves, and the alias table.
_NAME_TO_CODE: dict[str, str] = {}
for _code, _name in CANONICAL.items():
    _NAME_TO_CODE[_name.lower()] = _code
    _NAME_TO_CODE[_code.lower()] = _code
_NAME_TO_CODE.update(_ALIASES)


class UnknownJurisdiction(ValueError):
    """Raised when a label cannot be mapped to a canonical jurisdiction."""


def normalize_code(label: str) -> str:
    """Map any state or territory label to its canonical two-letter code.

    Strips whitespace and footnote markers, then matches against the alias
    table. Raises UnknownJurisdiction for anything outside the 50 states,
    DC, and the three tracked territories (for example, a US total row).
    """
    if label is None:
        raise UnknownJurisdiction("empty label")
    cleaned = label.strip()
    # Drop common footnote markers and trailing punctuation.
    for marker in ("*", "†", "‡", "1", "2", "3"):
        if cleaned.endswith(marker) and len(cleaned) > 2:
            cleaned = cleaned[: -len(marker)].strip()
    key = cleaned.lower()
    if key in _NAME_TO_CODE:
        return _NAME_TO_CODE[key]
    raise UnknownJurisdiction(label)


def try_normalize_code(label: str):
    """Like normalize_code, but returns None instead of raising.

    Useful when iterating raw rows that include national totals or notes
    that should be skipped rather than treated as a jurisdiction.
    """
    try:
        return normalize_code(label)
    except UnknownJurisdiction:
        return None


def is_territory(code: str) -> bool:
    return code in TERRITORIES


def display_name(code: str) -> str:
    return CANONICAL[code]


def ranking_codes() -> list[str]:
    """The 51 codes eligible for ranking, alphabetical by display name."""
    return sorted(RANKING_JURISDICTIONS, key=lambda c: RANKING_JURISDICTIONS[c])


def all_codes() -> list[str]:
    """All tracked codes (51 plus territories), alphabetical by name."""
    return sorted(CANONICAL, key=lambda c: CANONICAL[c])
