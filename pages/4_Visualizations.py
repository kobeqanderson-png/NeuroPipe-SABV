"""
Page 4: General Visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.branding import apply_subtle_branding
except ModuleNotFoundError:
    def apply_subtle_branding(*args, **kwargs):
        return None
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(page_title="NeuroPipe-SABV | Visualizations", page_icon=None, layout="wide")

apply_global_chrome()
render_top_navigation("Visualize")

st.title("General Visualizations")

if st.session_state.df_processed is None:
    st.warning("No processed data available. Please run the **Process Data** pipeline first.")
    st.stop()

df_processed = st.session_state.df_processed

st.markdown("""
Create publication-ready visualizations of your data including histograms, box plots, and correlation heatmaps.
""")

st.divider()

def render_branded_figure(fig) -> None:
    """Render figure after applying subtle attribution mark."""
    apply_subtle_branding(
        fig,
        enabled=st.session_state.get("branding_enabled", False),
        text_alpha=0.02,
        logo_alpha=0.03,
    )
    st.pyplot(fig)

numeric_cols = df_processed.select_dtypes(include=['number']).columns.tolist()

# Histogram and Box Plot
st.header("Single Variable Visualizations")

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.subheader("Histogram")
    if numeric_cols:
        hist_col = st.selectbox("Select column for histogram", numeric_cols, key="hist")

        fig, ax = plt.subplots(figsize=(8, 4))
        df_processed[hist_col].dropna().hist(bins=30, ax=ax, edgecolor='black', alpha=0.7, color='#22c55e')
        ax.set_title(f'Distribution of {hist_col}')
        ax.set_xlabel(hist_col)
        ax.set_ylabel('Frequency')
        render_branded_figure(fig)
        plt.close()

with viz_col2:
    st.subheader("Box Plot")
    if numeric_cols:
        box_col = st.selectbox("Select column for box plot", numeric_cols, key="box")

        fig, ax = plt.subplots(figsize=(8, 4))
        df_processed.boxplot(column=box_col, ax=ax)
        ax.set_title(f'Box Plot of {box_col}')
        render_branded_figure(fig)
        plt.close()

st.divider()

# Correlation heatmap
st.header("Correlation Analysis")
st.subheader("Correlation Heatmap")

numeric_df = df_processed.select_dtypes(include=['number'])
if len(numeric_df.columns) > 1:
    # Limit columns for readability
    max_cols = st.slider("Max columns to show", 5, min(20, len(numeric_df.columns)), 10)
    cols_to_plot = numeric_df.columns[:max_cols]

    fig, ax = plt.subplots(figsize=(12, 8))
    corr_matrix = numeric_df[cols_to_plot].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f', ax=ax, square=True)
    ax.set_title('Correlation Matrix')
    plt.tight_layout()
    render_branded_figure(fig)
    plt.close()
else:
    st.warning("Not enough numeric columns for correlation analysis")

st.divider()

# Advanced visualizations if Sex column exists
if 'Sex' in df_processed.columns:
    st.header("Sex-Based Visualizations")
    
    # Combined bar + scatter
    st.subheader("Combined Bar + Scatter")
    
    if numeric_cols:
        combo_var = st.selectbox(
            "Select variable for combined bar + scatter",
            numeric_cols,
            key="combo_var"
        )
        
        fig, ax = plt.subplots(figsize=(10, 6))
        barplot_common = {
            'data': df_processed,
            'x': 'Sex',
            'y': combo_var,
            'order': ['Male', 'Female'],
            'estimator': np.mean,
            'palette': ['#3498db', '#e74c3c'],
            'alpha': 0.75,
            'ax': ax,
        }
        try:
            sns.barplot(errorbar=('ci', 95), **barplot_common)
        except TypeError:
            sns.barplot(ci=95, **barplot_common)
        
        sns.stripplot(
            data=df_processed,
            x='Sex',
            y=combo_var,
            order=['Male', 'Female'],
            color='black',
            alpha=0.5,
            jitter=0.18,
            size=4,
            ax=ax
        )
        ax.set_title(f'{combo_var}: Mean Bar with Sample Scatter')
        ax.set_xlabel('Sex')
        ax.set_ylabel(combo_var)
        render_branded_figure(fig)
        plt.close()

    # Density distribution (KDE)
    st.subheader("Density Distribution")
    
    if numeric_cols:
        density_var = st.selectbox(
            "Select variable for density distribution",
            numeric_cols,
            key="density_var"
        )
        
        fig, ax = plt.subplots(figsize=(10, 5))
        male_density = df_processed[df_processed['Sex'] == 'Male'][density_var].dropna()
        female_density = df_processed[df_processed['Sex'] == 'Female'][density_var].dropna()

        if len(male_density) > 1:
            sns.kdeplot(male_density, fill=True, alpha=0.4, label='Male', color='#3498db', ax=ax)
        if len(female_density) > 1:
            sns.kdeplot(female_density, fill=True, alpha=0.4, label='Female', color='#e74c3c', ax=ax)

        ax.set_title(f'{density_var} Density by Sex')
        ax.set_xlabel(density_var)
        ax.set_ylabel('Density')
        if len(male_density) > 1 or len(female_density) > 1:
            ax.legend()
        else:
            st.info(
                f"Not enough values to estimate density for {density_var}. "
                "Need at least 2 non-missing values per group."
            )
        render_branded_figure(fig)
        plt.close()

    # Scatter plot
    st.subheader("Bivariate Scatter Plot")
    
    if len(numeric_cols) >= 2:
        scatter_cols = st.columns(2)
        with scatter_cols[0]:
            x_var = st.selectbox("X-axis variable", numeric_cols, key="scatter_x")
        with scatter_cols[1]:
            y_candidates = [c for c in numeric_cols if c != x_var] or numeric_cols
            y_var = st.selectbox("Y-axis variable", y_candidates, key="scatter_y")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=df_processed,
            x=x_var,
            y=y_var,
            hue='Sex',
            palette={'Male': '#3498db', 'Female': '#e74c3c'},
            alpha=0.75,
            s=60,
            ax=ax
        )
        ax.set_title(f'{y_var} vs {x_var} by Sex')
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        ax.legend(title='Sex')
        render_branded_figure(fig)
        plt.close()

st.divider()
st.info("Visualizations ready. Proceed to other pages for additional analysis and downloads.")
