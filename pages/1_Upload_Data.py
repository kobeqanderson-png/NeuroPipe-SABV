"""
Page 1: Upload and Explore Raw Data
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_load import read_csv, read_excel
from src.animations import (
    inject_animation_css,
    animated_header,
    animated_success_message,
    animated_info_message,
    animated_warning_message,
)
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(page_title="NeuroPipe-SABV | Upload Data", page_icon=None, layout="wide")

# Inject animations
inject_animation_css()
apply_global_chrome()
render_top_navigation("Upload")

animated_header("Upload Your Data", "Start by uploading a CSV or Excel file to begin analysis")
uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    help="Drag and drop or click to upload"
)

if uploaded_file is not None:
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension == '.csv':
            df_raw = read_csv(uploaded_file)
        elif file_extension in ['.xlsx', '.xls']:
            xl = pd.ExcelFile(uploaded_file)
            available_sheets = xl.sheet_names
            st.info(f"Available sheets: {', '.join(available_sheets)}")
            
            # Use sheet_name from session if exists, otherwise use first
            selected_sheet = st.selectbox("Select sheet to load", available_sheets, index=0)
            df_raw = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.session_state.df_raw = df_raw
        st.session_state.uploaded_filename = uploaded_file.name
        st.success(f"Loaded **{uploaded_file.name}** - {len(df_raw):,} rows x {len(df_raw.columns)} columns")
        
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

# Data exploration section
if st.session_state.df_raw is not None:
    df_raw = st.session_state.df_raw

    st.divider()
    st.header("Explore Raw Data")

    # Data preview tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Statistics", "Missing Values", "Columns"])

    with tab1:
        st.subheader("Data Preview")
        n_rows = st.slider("Rows to display", 5, 50, 10)
        st.dataframe(df_raw.head(n_rows), use_container_width=True)

    with tab2:
        st.subheader("Summary Statistics")
        numeric_cols = df_raw.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.dataframe(df_raw[numeric_cols].describe(), use_container_width=True)
        else:
            st.warning("No numeric columns found")

    with tab3:
        st.subheader("Missing Values")
        missing = df_raw.isnull().sum()
        missing_pct = (missing / len(df_raw) * 100).round(2)
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing Count': missing.values,
            'Missing %': missing_pct.values
        }).sort_values('Missing Count', ascending=False)

        missing_with_values = missing_df[missing_df['Missing Count'] > 0]
        if len(missing_with_values) > 0:
            st.dataframe(missing_with_values, use_container_width=True)
        else:
            st.success("No missing values found")

    with tab4:
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df_raw.columns,
            'Type': df_raw.dtypes.astype(str).values,
            'Non-Null Count': df_raw.notna().sum().values,
            'Unique Values': df_raw.nunique().values
        })
        st.dataframe(col_info, use_container_width=True)

    st.divider()
    st.info("Data loaded successfully! Proceed to the Process Data page to clean and classify your data.")

else:
    st.info("Upload a data file above to get started.")
