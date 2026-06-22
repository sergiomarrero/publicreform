"""Known-good anchors used by the validation gate.

These values come from docs/LANDSCAPE_BRIEF.md and docs/BUILD_SPEC.md. The
validator compares freshly fetched values against these anchors before any
UI-facing JSON is written. If a fetch matches the wrong vintage (for example
WIOA PY2024 when PY2023 was requested), the gate fails loudly.

Nothing here is rendered as a published number on its own; these are
verification references for the build, each tied to an explicit vintage.
"""

from __future__ import annotations

# Tolerances for floating point comparison against published tables.
SNAP_TOLERANCE = 0.01          # percentage points
WIOA_PCT_TOLERANCE = 0.3       # percentage points on a national headline rate
WIOA_EARNINGS_TOLERANCE = 50   # dollars on a national median earnings figure

# ---------------------------------------------------------------------------
# SNAP Application Processing Timeliness, FY2024, USDA FNS.
# Full published ordering transcribed from docs/LANDSCAPE_BRIEF.md Part B2.
# Percent of applications processed timely. Includes two territories
# (U.S. Virgin Islands, Guam) that are flagged and excluded from ranking.
# ---------------------------------------------------------------------------
SNAP_APT_FY2024 = {
    "Wisconsin": 95.62,
    "Illinois": 93.56,
    "Rhode Island": 93.52,
    "Nevada": 93.09,
    "Alabama": 93.02,
    "Ohio": 91.93,
    "Maryland": 91.04,
    "Idaho": 91.02,
    "Wyoming": 90.43,
    "Washington": 90.36,
    "Arizona": 90.29,
    "Pennsylvania": 90.29,
    "Utah": 89.82,
    "New Hampshire": 89.32,
    "Connecticut": 89.11,
    "Nebraska": 88.96,
    "Oklahoma": 88.65,
    "Kentucky": 87.38,
    "Louisiana": 87.08,
    "South Dakota": 85.89,
    "Massachusetts": 85.45,
    "Vermont": 84.47,
    "North Carolina": 84.40,
    "Virginia": 83.23,
    "Kansas": 81.99,
    "New York": 81.61,
    "Minnesota": 80.37,
    "California": 80.21,
    "Indiana": 80.04,
    "Mississippi": 79.38,
    "Missouri": 78.28,
    "U.S. Virgin Islands": 77.63,
    "New Jersey": 77.61,
    "Michigan": 76.05,
    "West Virginia": 75.80,
    "Texas": 75.48,
    "Delaware": 75.08,
    "South Carolina": 73.48,
    "Oregon": 71.83,
    "Hawaii": 68.87,
    "Georgia": 67.22,
    "Montana": 66.88,
    "Colorado": 66.87,
    "Maine": 64.93,
    "Iowa": 64.66,
    "Florida": 63.31,
    "Arkansas": 61.94,
    "Alaska": 57.93,
    "North Dakota": 57.02,
    "District of Columbia": 56.73,
    "New Mexico": 52.36,
    "Guam": 50.86,
    "Tennessee": 42.72,
}

# Spot anchors the gate checks explicitly (BUILD_SPEC Stage 1 validation).
SNAP_SPOT_ANCHORS = {
    "Wisconsin": 95.62,        # published maximum
    "Tennessee": 42.72,        # published minimum
    "District of Columbia": 56.73,
    "California": 80.21,
}

SNAP_PUBLISHED_MAX = ("Wisconsin", 95.62)
SNAP_PUBLISHED_MIN = ("Tennessee", 42.72)
SNAP_CORRECTIVE_ACTION_THRESHOLD = 90.0  # below this, state must act

# ---------------------------------------------------------------------------
# WIOA national headline indicators.
# PY2023 is the target vintage for v1. PY2024 is recorded only so the gate
# can detect a vintage swap (the live At-A-Glance page now serves PY2024).
# Source: docs/LANDSCAPE_BRIEF.md Part B3.
# ---------------------------------------------------------------------------
WIOA_PY2023_NATIONAL = {
    "adult": {
        "emp_q2": 74.1,
        "emp_q4": 73.4,
        "median_earnings_q2": 8677,
        "credential": 72.2,
        "measurable_skill_gains": 71.2,
    },
    "dislocated_worker": {
        "emp_q2": 70.7,
        "emp_q4": 71.4,
        "median_earnings_q2": 9397,
        "credential": 73.5,
        "measurable_skill_gains": 70.4,
    },
}

# Reference only. If a fetch matches these instead of PY2023, the gate fails
# with a vintage mismatch error.
WIOA_PY2024_NATIONAL = {
    "adult": {
        "emp_q2": 72.2,
        "emp_q4": 72.3,
        "median_earnings_q2": 8754,
        "credential": 73.6,
        "measurable_skill_gains": 74.0,
    },
    "dislocated_worker": {
        "emp_q2": 69.0,
        "emp_q4": 70.5,
        "median_earnings_q2": 9897,
        "credential": 75.1,
        "measurable_skill_gains": 72.4,
    },
}

# The two figures the spec calls out by name for the PY2023 gate.
WIOA_ANCHOR_ADULT_EMP_Q2 = 74.1
WIOA_ANCHOR_DW_MEDIAN_EARNINGS = 9397

# UI ETA 9050 federal Secretary's Standard: 87% of intrastate first payments
# within 14/21 days. Used as the flag threshold, not as a value anchor.
UI_SECRETARYS_STANDARD = 87.0
