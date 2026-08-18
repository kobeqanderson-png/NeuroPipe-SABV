"""Basic cleaning pipeline functions with header standardization.

Example usage:
    from src.cleaning import basic_clean
    df = pd.read_csv('data/raw/sample.csv')
    df_clean, report = basic_clean(df, standardize=True)
    # df_clean has canonical column names and cleaned data
    # report shows header renames and any artifact flags
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional

try:
    from src.header_mapping import standardize_headers
    _HAS_HEADER_MAPPING = True
except ImportError:
    _HAS_HEADER_MAPPING = False

try:
    from src.artifact_detection import detect_artifacts
    _HAS_ARTIFACT_DETECTION = True
except ImportError:
    _HAS_ARTIFACT_DETECTION = False


def basic_clean(
    df: pd.DataFrame,
    date_cols: List[str] = None,
    id_cols: List[str] = None,
    standardize: bool = True,
    detect_artifacts_flag: bool = False,
    artifact_kwargs: Optional[Dict] = None,
) -> Tuple[pd.DataFrame, Dict]:
    """Perform common cleaning steps with optional header standardization.

    Operations (in order):
    1. Strip column names
    2. Optional: standardize headers to canonical vocabulary
    3. Parse date columns
    4. Drop rows missing required IDs
    5. Drop exact duplicates
    6. Fill numeric NaNs with median
    7. Trim string columns
    8. Optional: detect tracking artifacts

    Args:
        df: input DataFrame
        date_cols: list of columns to parse as dates
        id_cols: list of columns that must not be null (drop rows missing these)
        standardize: whether to run header standardization
        detect_artifacts_flag: whether to run artifact detection
        artifact_kwargs: dict passed to detect_artifacts()

    Returns:
        (cleaned DataFrame, report dict)
    """
    report = {"original_shape": df.shape}

    # 1. Strip column names
    df = df.copy()
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # 2. Header standardization
    if standardize and _HAS_HEADER_MAPPING:
        df, header_report = standardize_headers(df, unmatched_strategy="keep")
        report["header_standardization"] = header_report
    else:
        report["header_standardization"] = {"skipped": not standardize or not _HAS_HEADER_MAPPING}

    # 3. Parse dates
    if date_cols:
        for c in date_cols:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors='coerce')

    # 4. Drop rows missing required ids
    if id_cols:
        present_id_cols = [c for c in id_cols if c in df.columns]
        if present_id_cols:
            before = len(df)
            df = df.dropna(subset=present_id_cols)
            report["dropped_missing_id"] = before - len(df)

    # 5. Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    report["dropped_duplicates"] = before - len(df)

    # 6. Simple numeric imputation: fill NaN with median
    num_cols = df.select_dtypes(include=['number']).columns
    for c in num_cols:
        med = df[c].median()
        if pd.notna(med):
            df[c] = df[c].fillna(med)

    # 7. Trim string columns and fill NA with empty string
    obj_cols = df.select_dtypes(include=['object']).columns
    for c in obj_cols:
        df[c] = df[c].astype(str).str.strip().replace({'nan': ''})

    # 8. Artifact detection
    if detect_artifacts_flag and _HAS_ARTIFACT_DETECTION:
        artifact_report = detect_artifacts(df, **(artifact_kwargs or {}))
        report["artifact_detection"] = artifact_report["summary"]
        report["artifact_recommendations"] = artifact_report["recommendations"]
    else:
        report["artifact_detection"] = {"skipped": not detect_artifacts_flag or not _HAS_ARTIFACT_DETECTION}

    report["final_shape"] = df.shape
    return df, report


def save_clean(df: pd.DataFrame, path_csv: str = None, path_parquet: str = None) -> None:
    """Save cleaned DataFrame to CSV and/or parquet as requested."""
    if path_csv:
        df.to_csv(path_csv, index=False)
    if path_parquet:
        df.to_parquet(path_parquet, index=False)
