"""
Page 2: Process Data - Clean and Classify
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import re

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.cleaning import basic_clean
from src.features import add_log_feature
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(page_title="NeuroPipe-SABV | Process Data", page_icon=None, layout="wide")

apply_global_chrome()
render_top_navigation("Process")

st.title("Process Data")

if st.session_state.df_raw is None:
    st.warning("No data loaded. Please upload a file in the **Upload Data** page first.")
    st.stop()

df_raw = st.session_state.df_raw

st.markdown("""
Clean your data and apply sex classification based on animal ID numbers.
""")

st.divider()

# Helper functions for ID parsing
def parse_animal_number(value) -> float:
    """Extract animal ID numbers from numeric values or labels like 'rat17'/'subject_17'."""
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip()
    if not text:
        return np.nan

    lower_text = text.lower()

    prefixed_match = re.search(
        r"(?:rat|subject|animal)\s*[-_#:]?\s*(\d+(?:\.\d+)?)",
        lower_text,
    )
    if prefixed_match:
        return float(prefixed_match.group(1))

    numeric_only_match = re.fullmatch(r"\d+(?:\.\d+)?", lower_text)
    if numeric_only_match:
        return float(numeric_only_match.group(0))

    match = re.search(r"\d+(?:\.\d+)?", text)
    if match:
        return float(match.group(0))
    return np.nan


def parse_animal_number_series(series: pd.Series) -> pd.Series:
    """Vectorized animal-number parsing for mixed numeric/text identifiers."""
    return series.apply(parse_animal_number)


def parse_id_list(raw_text: str):
    """Parse comma-separated IDs/ranges (e.g., '1-16, 20, 22-24') into numeric IDs."""
    values = set()
    invalid_tokens = []

    for token in raw_text.split(','):
        token = token.strip()
        if not token:
            continue

        if '-' in token:
            parts = token.split('-', 1)
            if len(parts) != 2:
                invalid_tokens.append(token)
                continue
            try:
                start = float(parts[0].strip())
                end = float(parts[1].strip())
            except ValueError:
                invalid_tokens.append(token)
                continue

            if float(start).is_integer() and float(end).is_integer():
                start_i = int(start)
                end_i = int(end)
                lo, hi = (start_i, end_i) if start_i <= end_i else (end_i, start_i)
                for v in range(lo, hi + 1):
                    values.add(float(v))
            else:
                values.add(float(start))
                values.add(float(end))
            continue

        try:
            values.add(float(token))
        except ValueError:
            invalid_tokens.append(token)

    return values, invalid_tokens


# Dynamic Column Selection
all_cols = df_raw.columns.tolist()

col_a, col_b = st.columns(2)
with col_a:
    sex_col = st.selectbox(
        "Select Column for Sex Classification", 
        options=all_cols,
        help="Select the ID column (e.g., 1, animal_1, rat1, subject1)."
    )

with col_b:
    classification_mode = st.radio(
        "Classification Method",
        ["Threshold split", "Manual number lists", "Female list (others Male)"],
        horizontal=True,
    )

threshold = st.session_state.get('sex_threshold', 16)
male_ids_text = ""
female_ids_text = ""

if classification_mode == "Threshold split":
    threshold = st.number_input(
        f"Threshold for {sex_col}",
        value=threshold,
        step=1,
        help="Animal ID <= threshold is Male; > threshold is Female.",
    )
elif classification_mode == "Manual number lists":
    st.caption("Enter comma-separated IDs or ranges like 1-16, 20, 22-24.")
    list_col_a, list_col_b = st.columns(2)
    with list_col_a:
        male_ids_text = st.text_input("Male IDs", value="1-16")
    with list_col_b:
        female_ids_text = st.text_input("Female IDs", value="17-32")
else:
    st.caption("Enter female IDs; any other numeric ID will be assigned Male.")
    female_ids_text = st.text_input("Female IDs", value="17-32")

st.divider()

if st.button("Run Processing Pipeline", type="primary", use_container_width=True):
    with st.spinner("Processing data..."):
        try:
            # 1. Apply basic cleaning
            df_processed = basic_clean(df_raw)
            
            # 2. Apply sex classification
            sex_numeric = parse_animal_number_series(df_processed[sex_col])
            if classification_mode == "Threshold split":
                df_processed['Sex'] = np.where(
                    sex_numeric <= threshold,
                    'Male',
                    np.where(sex_numeric > threshold, 'Female', 'Unclassified')
                )
            elif classification_mode == "Manual number lists":
                male_ids, male_invalid = parse_id_list(male_ids_text)
                female_ids, female_invalid = parse_id_list(female_ids_text)

                if male_invalid or female_invalid:
                    bad_tokens = male_invalid + female_invalid
                    raise ValueError(
                        f"Invalid ID tokens: {', '.join(bad_tokens)}. Use numbers or ranges like 1-16, 20."
                    )

                overlap = male_ids.intersection(female_ids)
                if overlap:
                    st.warning(
                        f"Overlapping IDs in male/female lists: {sorted(overlap)}. Male assignment takes precedence."
                    )

                male_mask = sex_numeric.isin(male_ids)
                female_mask = sex_numeric.isin(female_ids)
                df_processed['Sex'] = np.select(
                    [male_mask, female_mask],
                    ['Male', 'Female'],
                    default='Unclassified',
                )
            else:
                female_ids, female_invalid = parse_id_list(female_ids_text)
                if female_invalid:
                    raise ValueError(
                        f"Invalid ID tokens: {', '.join(female_invalid)}. Use numbers or ranges like 17-32, 40."
                    )

                is_numeric_id = sex_numeric.notna()
                female_mask = sex_numeric.isin(female_ids)
                df_processed['Sex'] = np.select(
                    [female_mask, is_numeric_id],
                    ['Female', 'Male'],
                    default='Unclassified',
                )

            unclassified_count = int((df_processed['Sex'] == 'Unclassified').sum())
            if unclassified_count > 0:
                st.warning(
                    f"{unclassified_count} row(s) could not be classified because no numeric animal ID was found in '{sex_col}'."
                )
            
            st.session_state.sex_col_used = sex_col
            st.session_state.sex_threshold_used = float(threshold)
            st.session_state.sex_rebuild_from_threshold = classification_mode == "Threshold split"
            
            # 3. Add log features if enabled
            if st.session_state.get('add_log', True):
                numeric_cols = df_processed.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    df_processed = add_log_feature(df_processed, col=numeric_cols[0])
            
            # 4. Save results
            st.session_state.df_processed = df_processed
            st.success("Processing complete!")
            
            st.divider()
            st.info("Data ready for analysis. Proceed to the **Sex Analysis** page to explore differences.")
            
        except Exception as e:
            st.error(f"Error during processing: {e}")

# Show processing summary if data has been processed
if st.session_state.get('df_processed') is not None:
    st.divider()
    st.subheader("Processing Summary")
    df_proc = st.session_state.df_processed
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", len(df_proc))
    with col2:
        males = (df_proc['Sex'] == 'Male').sum()
        st.metric("Males", males)
    with col3:
        females = (df_proc['Sex'] == 'Female').sum()
        st.metric("Females", females)
    
    st.dataframe(df_proc.head(10), use_container_width=True)
