"""Artifact detection for preclinical behavioral tracking data.

Flags common data quality issues in video-tracking exports:
- Velocity spikes (physiologically impossible speeds)
- Tracking dropouts (repeated identical coordinates)
- Coordinate jumps (teleportation artifacts)
- Missing-value patterns
- Out-of-bounds coordinates

Usage:
    from src.artifact_detection import detect_artifacts
    report = detect_artifacts(df, x_col="x_center", y_col="y_center",
                               velocity_col="velocity", animal_col="animal_id")
    # report is a dict with flagged rows, summary stats, and recommendations
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Default thresholds (rodent-appropriate, configurable)
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLDS = {
    "max_velocity_m_per_s": 2.0,          # ~2 m/s is fast for a rodent
    "min_velocity_m_per_s": 0.0,           # negative speeds are impossible
    "max_coordinate_jump_m": 0.5,          # 50 cm in one frame is suspicious
    "max_consecutive_identical_frames": 5, # frozen coordinates for 5+ frames
    "out_of_bounds_tolerance": 0.01,     # 1% outside arena bounds
}


# ---------------------------------------------------------------------------
# Detection functions
# ---------------------------------------------------------------------------

def _detect_velocity_spikes(
    df: pd.DataFrame,
    velocity_col: str,
    max_vel: float,
    min_vel: float,
) -> pd.Series:
    """Flag rows where velocity exceeds physiological bounds."""
    if velocity_col not in df.columns:
        return pd.Series(False, index=df.index)
    vel = pd.to_numeric(df[velocity_col], errors="coerce")
    return (vel > max_vel) | (vel < min_vel)


def _detect_tracking_dropouts(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    animal_col: str,
    max_identical: int,
) -> pd.Series:
    """Flag rows where coordinates are identical for too many consecutive frames.

    This catches camera/frame-grabber failures where the animal is reported
    at the exact same pixel for multiple frames.
    """
    if x_col not in df.columns or y_col not in df.columns:
        return pd.Series(False, index=df.index)

    flagged = pd.Series(False, index=df.index)

    # Group by animal if available, otherwise treat as single sequence
    groups = [df] if animal_col not in df.columns else [g for _, g in df.groupby(animal_col)]

    for group in groups:
        idx = group.index
        x = pd.to_numeric(group[x_col], errors="coerce")
        y = pd.to_numeric(group[y_col], errors="coerce")

        # Detect consecutive identical (x, y) pairs
        same_xy = (x == x.shift(1)) & (y == y.shift(1))
        # Run-length encoding: count consecutive Trues
        run_id = (~same_xy).cumsum()
        run_lengths = same_xy.groupby(run_id).transform("sum") + 1
        flagged.loc[idx] |= (same_xy & (run_lengths >= max_identical))

    return flagged


def _detect_coordinate_jumps(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    animal_col: str,
    max_jump: float,
) -> pd.Series:
    """Flag rows where the animal teleports an implausible distance between frames."""
    if x_col not in df.columns or y_col not in df.columns:
        return pd.Series(False, index=df.index)

    flagged = pd.Series(False, index=df.index)
    groups = [df] if animal_col not in df.columns else [g for _, g in df.groupby(animal_col)]

    for group in groups:
        idx = group.index
        x = pd.to_numeric(group[x_col], errors="coerce")
        y = pd.to_numeric(group[y_col], errors="coerce")

        dx = x.diff().abs()
        dy = y.diff().abs()
        jump = np.sqrt(dx**2 + dy**2)
        flagged.loc[idx] |= jump > max_jump

    return flagged


def _detect_missing_patterns(
    df: pd.DataFrame,
    required_cols: List[str],
) -> pd.Series:
    """Flag rows with missing values in required tracking columns."""
    cols = [c for c in required_cols if c in df.columns]
    if not cols:
        return pd.Series(False, index=df.index)
    return df[cols].isna().any(axis=1)


def _detect_out_of_bounds(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    arena_bounds: Optional[Tuple[float, float, float, float]] = None,
) -> pd.Series:
    """Flag rows where coordinates fall outside the defined arena.

    arena_bounds = (x_min, x_max, y_min, y_max)
    If None, uses 2-sigma heuristic around the mean.
    """
    if x_col not in df.columns or y_col not in df.columns:
        return pd.Series(False, index=df.index)

    x = pd.to_numeric(df[x_col], errors="coerce")
    y = pd.to_numeric(df[y_col], errors="coerce")

    if arena_bounds is not None:
        x_min, x_max, y_min, y_max = arena_bounds
        return (x < x_min) | (x > x_max) | (y < y_min) | (y > y_max)
    else:
        # Heuristic: flag values > 3 standard deviations from mean
        x_mean, x_std = x.mean(), x.std()
        y_mean, y_std = y.mean(), y.std()
        x_out = np.abs(x - x_mean) > 3 * x_std
        y_out = np.abs(y - y_mean) > 3 * y_std
        return x_out | y_out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_artifacts(
    df: pd.DataFrame,
    x_col: str = "x_center",
    y_col: str = "y_center",
    velocity_col: str = "velocity",
    animal_col: str = "animal_id",
    arena_bounds: Optional[Tuple[float, float, float, float]] = None,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict:
    """Run the full artifact detection pipeline on a tracking DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw or cleaned tracking data.
    x_col, y_col : str
        Column names for spatial coordinates.
    velocity_col : str
        Column name for velocity/speed.
    animal_col : str
        Column name for animal/subject identifier.
    arena_bounds : tuple or None
        (x_min, x_max, y_min, y_max) in meters. If None, uses 3-sigma heuristic.
    thresholds : dict or None
        Override default thresholds.

    Returns
    -------
    report : dict
        {
            "flagged_rows": pd.Series[bool],
            "summary": {
                "total_rows": int,
                "velocity_spikes": int,
                "tracking_dropouts": int,
                "coordinate_jumps": int,
                "missing_required": int,
                "out_of_bounds": int,
                "any_flag": int,
                "flag_rate": float,
            },
            "recommendations": [str, ...],
            "flagged_df": pd.DataFrame,  # subset of rows with any flag
        }
    """
    th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    # Run detectors
    vel_flags = _detect_velocity_spikes(
        df, velocity_col, th["max_velocity_m_per_s"], th["min_velocity_m_per_s"]
    )
    dropout_flags = _detect_tracking_dropouts(
        df, x_col, y_col, animal_col, th["max_consecutive_identical_frames"]
    )
    jump_flags = _detect_coordinate_jumps(
        df, x_col, y_col, animal_col, th["max_coordinate_jump_m"]
    )
    missing_flags = _detect_missing_patterns(
        df, [x_col, y_col, velocity_col, animal_col]
    )
    bounds_flags = _detect_out_of_bounds(df, x_col, y_col, arena_bounds)

    any_flag = vel_flags | dropout_flags | jump_flags | missing_flags | bounds_flags

    total = len(df)
    any_count = any_flag.sum()

    recommendations: List[str] = []
    if vel_flags.sum() > 0:
        recommendations.append(
            f"{vel_flags.sum()} rows have impossible velocities. "
            "Check camera frame rate calibration or smoothing settings."
        )
    if dropout_flags.sum() > 0:
        recommendations.append(
            f"{dropout_flags.sum()} rows show tracking dropouts (frozen coordinates). "
            "Consider interpolation or excluding affected time bins."
        )
    if jump_flags.sum() > 0:
        recommendations.append(
            f"{jump_flags.sum()} rows have coordinate jumps. "
            "Likely identity-swap or tracking loss between frames."
        )
    if missing_flags.sum() > 0:
        recommendations.append(
            f"{missing_flags.sum()} rows have missing required values. "
            "Verify export settings include all tracking channels."
        )
    if bounds_flags.sum() > 0:
        recommendations.append(
            f"{bounds_flags.sum()} rows are outside arena bounds. "
            "Check arena definition or calibration."
        )

    summary = {
        "total_rows": total,
        "velocity_spikes": int(vel_flags.sum()),
        "tracking_dropouts": int(dropout_flags.sum()),
        "coordinate_jumps": int(jump_flags.sum()),
        "missing_required": int(missing_flags.sum()),
        "out_of_bounds": int(bounds_flags.sum()),
        "any_flag": int(any_count),
        "flag_rate": round(any_count / total, 4) if total > 0 else 0.0,
    }

    return {
        "flagged_rows": any_flag,
        "summary": summary,
        "recommendations": recommendations,
        "flagged_df": df[any_flag].copy() if any_count > 0 else pd.DataFrame(),
        "detail": {
            "velocity_spike_rows": df.index[vel_flags].tolist(),
            "dropout_rows": df.index[dropout_flags].tolist(),
            "jump_rows": df.index[jump_flags].tolist(),
            "missing_rows": df.index[missing_flags].tolist(),
            "bounds_rows": df.index[bounds_flags].tolist(),
        },
    }
