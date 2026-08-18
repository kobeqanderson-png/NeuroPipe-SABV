"""Header standardization for EthoVision XT and ANY-maze CSV exports.

Normalizes inconsistent column names across export formats so downstream
analysis can refer to a single canonical vocabulary.

Usage:
    from src.header_mapping import standardize_headers
    df = pd.read_csv("ethovision_export.csv")
    df, report = standardize_headers(df)
    # df now has canonical column names
    # report shows what was renamed and what could not be matched
"""

from __future__ import annotations

import difflib
import re
from typing import Dict, List, Tuple

import pandas as pd


# ---------------------------------------------------------------------------
# Canonical vocabulary — the names downstream code expects
# ---------------------------------------------------------------------------

CANONICAL_NAMES = {
    # Identity
    "animal_id": [
        "animal",
        "animal id",
        "animal_id",
        "animalid",
        "subject",
        "subject id",
        "subject_id",
        "subjectid",
        "trial",
        "trial id",
        "trial_id",
        "trialid",
        "mouse",
        "mouse id",
        "mouse_id",
        "rat",
        "rat id",
        "rat_id",
        "id",
        "identifier",
    ],
    # Spatial tracking
    "x_center": [
        "x center",
        "x_center",
        "xcenter",
        "center x",
        "center_x",
        "x",
        "x coord",
        "x_coord",
        "x position",
        "x_position",
        "xpos",
    ],
    "y_center": [
        "y center",
        "y_center",
        "ycenter",
        "center y",
        "center_y",
        "y",
        "y coord",
        "y_coord",
        "y position",
        "y_position",
        "ypos",
    ],
    # Movement
    "distance_travelled": [
        "distance travelled",
        "distance_travelled",
        "distance traveled",
        "distance_traveled",
        "dist travelled",
        "dist_travelled",
        "dist traveled",
        "dist_traveled",
        "total distance",
        "total_distance",
        "distance",
        "path length",
        "path_length",
    ],
    "velocity": [
        "velocity",
        "speed",
        "mean velocity",
        "mean_velocity",
        "average velocity",
        "average_velocity",
        "avg velocity",
        "avg_velocity",
        "instantaneous speed",
        "instantaneous_speed",
    ],
    # Zone / region measures
    "time_in_zone": [
        "time in zone",
        "time_in_zone",
        "time in center",
        "time_in_center",
        "time in open",
        "time_in_open",
        "time in closed",
        "time_in_closed",
        "time in target",
        "time_in_target",
        "zone time",
        "zone_time",
        "duration in zone",
        "duration_in_zone",
    ],
    "entries_into_zone": [
        "entries",
        "zone entries",
        "zone_entries",
        "entries into zone",
        "entries_into_zone",
        "number of entries",
        "number_of_entries",
        "entry count",
        "entry_count",
    ],
    # Latency
    "latency": [
        "latency",
        "latency to first entry",
        "latency_to_first_entry",
        "latency to enter",
        "latency_to_enter",
        "time to first entry",
        "time_to_first_entry",
        "first entry latency",
        "first_entry_latency",
    ],
    # Body measures (common in preclinical)
    "weight": [
        "weight",
        "body weight",
        "body_weight",
        "mass",
        "body mass",
        "body_mass",
    ],
    "length": [
        "length",
        "body length",
        "body_length",
    ],
    # Temporal
    "time": [
        "time",
        "timestamp",
        "elapsed time",
        "elapsed_time",
        "recording time",
        "recording_time",
        "frame time",
        "frame_time",
    ],
    "frame": [
        "frame",
        "frame number",
        "frame_number",
        "frame no",
        "frame_no",
        "frame id",
        "frame_id",
    ],
}


# ---------------------------------------------------------------------------
# Build reverse lookup for fast exact matching
# ---------------------------------------------------------------------------

def _build_reverse_lookup(
    canonical_map: Dict[str, List[str]]
) -> Dict[str, str]:
    """Map every alias (lowercased, stripped) to its canonical key."""
    lookup: Dict[str, str] = {}
    for canonical, aliases in canonical_map.items():
        for alias in aliases:
            key = alias.strip().lower()
            lookup[key] = canonical
    return lookup


_REVERSE_LOOKUP = _build_reverse_lookup(CANONICAL_NAMES)


# ---------------------------------------------------------------------------
# Matching strategies
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """Lowercase, strip whitespace, collapse internal spaces, remove punctuation."""
    text = str(text).strip().lower()
    text = re.sub(r"[\s_]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text.strip()


def _exact_match(col: str, lookup: Dict[str, str]) -> str | None:
    """Try exact normalized match."""
    return lookup.get(_normalize_text(col))


def _fuzzy_match(
    col: str,
    lookup: Dict[str, str],
    cutoff: float = 0.85,
) -> str | None:
    """Try fuzzy match using difflib.SequenceMatcher."""
    norm_col = _normalize_text(col)
    candidates = list(lookup.keys())
    matches = difflib.get_close_matches(norm_col, candidates, n=1, cutoff=cutoff)
    if matches:
        return lookup[matches[0]]
    return None


def _substring_match(col: str, lookup: Dict[str, str]) -> str | None:
    """Try substring containment (e.g., 'Total distance travelled' contains 'distance travelled')."""
    norm_col = _normalize_text(col)
    for alias, canonical in lookup.items():
        if alias in norm_col or norm_col in alias:
            return canonical
    return None


def _match_column(col: str, lookup: Dict[str, str]) -> str | None:
    """Attempt exact → fuzzy → substring matching."""
    for matcher in (_exact_match, _fuzzy_match, _substring_match):
        result = matcher(col, lookup)
        if result is not None:
            return result
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def standardize_headers(
    df: pd.DataFrame,
    canonical_map: Dict[str, List[str]] | None = None,
    unmatched_strategy: str = "keep",
) -> Tuple[pd.DataFrame, Dict]:
    """Rename DataFrame columns to a canonical vocabulary.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with raw export column names.
    canonical_map : dict, optional
        Override the default CANONICAL_NAMES mapping.
    unmatched_strategy : {"keep", "drop", "warn"}
        What to do with columns that cannot be matched:
        - "keep": leave the original name (default)
        - "drop": remove the column
        - "warn": keep but flag in the report

    Returns
    -------
    df_renamed : pd.DataFrame
        DataFrame with canonical column names.
    report : dict
        Diagnostic report with keys:
        - "renamed": {original: canonical}
        - "unmatched": [original, ...]
        - "collisions": {canonical: [originals]}  # if multiple cols map to same canonical
        - "dropped": [original, ...]  # if unmatched_strategy="drop"
    """
    if canonical_map is None:
        canonical_map = CANONICAL_NAMES

    lookup = _build_reverse_lookup(canonical_map)
    renamed: Dict[str, str] = {}
    unmatched: List[str] = []
    collisions: Dict[str, List[str]] = {}
    dropped: List[str] = []

    new_columns: List[str] = []

    for col in df.columns:
        canonical = _match_column(col, lookup)
        if canonical:
            renamed[col] = canonical
            if canonical in collisions:
                collisions[canonical].append(col)
            else:
                collisions[canonical] = [col]
            new_columns.append(canonical)
        else:
            unmatched.append(col)
            if unmatched_strategy == "drop":
                dropped.append(col)
                continue
            new_columns.append(col)

    df_out = df.copy()
    df_out.columns = new_columns

    # Handle collisions: if multiple original columns map to the same canonical name,
    # append a suffix to disambiguate.
    seen: Dict[str, int] = {}
    final_columns: List[str] = []
    for c in new_columns:
        if c in seen:
            seen[c] += 1
            final_columns.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            final_columns.append(c)
    df_out.columns = final_columns

    report = {
        "renamed": renamed,
        "unmatched": unmatched,
        "collisions": {k: v for k, v in collisions.items() if len(v) > 1},
        "dropped": dropped,
    }

    return df_out, report


def get_canonical_vocabulary() -> List[str]:
    """Return the list of canonical column names."""
    return list(CANONICAL_NAMES.keys())


def add_alias(canonical_name: str, aliases: List[str]) -> None:
    """Dynamically add aliases to the canonical vocabulary at runtime.

    Useful for lab-specific export formats not covered by the default map.
    """
    if canonical_name not in CANONICAL_NAMES:
        CANONICAL_NAMES[canonical_name] = []
    CANONICAL_NAMES[canonical_name].extend(aliases)
    # Rebuild lookup
    global _REVERSE_LOOKUP
    _REVERSE_LOOKUP = _build_reverse_lookup(CANONICAL_NAMES)
