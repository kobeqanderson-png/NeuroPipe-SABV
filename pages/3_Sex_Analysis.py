"""
Page 3: Sex Differences Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as scipy_stats
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.branding import apply_subtle_branding, brand_label
except ModuleNotFoundError:
    def apply_subtle_branding(*args, **kwargs):
        return None
    def brand_label(default: str = "kobeanderson-png") -> str:
        return default
from src.navigation import apply_global_chrome, render_top_navigation

st.set_page_config(page_title="NeuroPipe-SABV | Sex Analysis", page_icon=None, layout="wide")

apply_global_chrome()
render_top_navigation("Sex Analysis")

st.title("Sex Differences Analysis")

if st.session_state.df_processed is None:
    st.warning("No processed data available. Please run the **Process Data** pipeline first.")
    st.stop()

df_processed = st.session_state.df_processed

if 'Sex' not in df_processed.columns:
    st.warning("No 'Sex' column found. Please run processing first.")
    st.stop()

st.markdown("""
Analyze and visualize sex differences in your data using statistical tests and comparisons.
""")

st.divider()

# Helper functions
def render_branded_figure(fig) -> None:
    """Render figure after applying subtle attribution mark."""
    apply_subtle_branding(
        fig,
        enabled=st.session_state.get("branding_enabled", False),
        text_alpha=0.02,
        logo_alpha=0.03,
    )
    st.pyplot(fig)

def safe_percent_diff(male_mean: float, female_mean: float) -> float:
    """Return percent difference relative to female mean; NaN if denominator is zero."""
    if pd.isna(female_mean) or female_mean == 0:
        return np.nan
    return (male_mean - female_mean) / female_mean * 100

def ttest_for_groups(df: pd.DataFrame, value_col: str, group_col: str = "Sex"):
    """Compute Welch's t-test between Male and Female groups for a variable."""
    male_data = df[df[group_col] == 'Male'][value_col].dropna()
    female_data = df[df[group_col] == 'Female'][value_col].dropna()

    if len(male_data) > 1 and len(female_data) > 1:
        t_stat, p_value = scipy_stats.ttest_ind(male_data, female_data, equal_var=False)
        return t_stat, p_value, len(male_data), len(female_data)
    return np.nan, np.nan, len(male_data), len(female_data)

def effect_size_cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """Calculate Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    
    if n1 < 2 or n2 < 2:
        return np.nan
    
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return np.nan
    
    return (group1.mean() - group2.mean()) / pooled_std

def pvalue_to_label(p_value: float) -> str:
    """Convert p-value to a readable significance label."""
    if pd.isna(p_value):
        return "Insufficient data"
    return "Significant" if p_value < 0.05 else "Not Significant"

def sem(series: pd.Series) -> float:
    """Calculate SEM = std(N) / sqrt(N) using sample std (ddof=1)."""
    values = series.dropna()
    n = len(values)
    if n < 2:
        return np.nan
    return values.std(ddof=1) / np.sqrt(n)

# Sex distribution overview
st.subheader("Sex Distribution")

sex_counts = df_processed['Sex'].value_counts()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Samples", len(df_processed))
with col2:
    male_count = sex_counts.get('Male', 0)
    st.metric("Males", male_count, f"{male_count/len(df_processed)*100:.1f}%")
with col3:
    female_count = sex_counts.get('Female', 0)
    st.metric("Females", female_count, f"{female_count/len(df_processed)*100:.1f}%")

# Sex distribution pie chart
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

colors = ['#3498db', '#e74c3c']
axes[0].pie(sex_counts.values, labels=sex_counts.index, autopct='%1.1f%%',
           colors=colors, startangle=90)
axes[0].set_title('Sex Distribution')

sex_counts.plot(kind='bar', ax=axes[1], color=colors, edgecolor='black')
axes[1].set_title('Sex Counts')
axes[1].set_xlabel('Sex')
axes[1].set_ylabel('Count')
axes[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
render_branded_figure(fig)
plt.close()

st.divider()

# Sex differences comparison
st.subheader("Compare Variables by Sex")

numeric_cols = df_processed.select_dtypes(include=['number']).columns.tolist()

if numeric_cols:
    selected_var = st.selectbox(
        "Select variable to compare between sexes",
        numeric_cols,
        key="sex_compare"
    )

    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # Box plot by sex
        fig, ax = plt.subplots(figsize=(8, 5))
        df_processed.boxplot(column=selected_var, by='Sex', ax=ax)
        ax.set_title(f'{selected_var} by Sex')
        ax.set_xlabel('Sex')
        ax.set_ylabel(selected_var)
        plt.suptitle('')
        render_branded_figure(fig)
        plt.close()

    with viz_col2:
        # Violin plot by sex
        fig, ax = plt.subplots(figsize=(8, 5))
        parts = ax.violinplot(
            [df_processed[df_processed['Sex'] == 'Male'][selected_var].dropna(),
             df_processed[df_processed['Sex'] == 'Female'][selected_var].dropna()],
            positions=[1, 2],
            showmeans=True,
            showmedians=True
        )
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Male', 'Female'])
        ax.set_title(f'{selected_var} Distribution by Sex')
        ax.set_xlabel('Sex')
        ax.set_ylabel(selected_var)
        render_branded_figure(fig)
        plt.close()

    # Histogram overlay by sex
    st.subheader("Distribution Overlay")
    fig, ax = plt.subplots(figsize=(10, 5))

    male_data = df_processed[df_processed['Sex'] == 'Male'][selected_var].dropna()
    female_data = df_processed[df_processed['Sex'] == 'Female'][selected_var].dropna()

    ax.hist(male_data, bins=20, alpha=0.6, label='Male', color='#3498db', edgecolor='black')
    ax.hist(female_data, bins=20, alpha=0.6, label='Female', color='#e74c3c', edgecolor='black')
    ax.set_title(f'{selected_var} Distribution by Sex')
    ax.set_xlabel(selected_var)
    ax.set_ylabel('Frequency')
    ax.legend()
    render_branded_figure(fig)
    plt.close()

    # Summary statistics by sex
    st.subheader("Summary Statistics by Sex")

    stats_by_sex = df_processed.groupby('Sex')[selected_var].agg([
        'count', 'mean', 'std', 'min', 'median', 'max'
    ]).round(4)
    stats_by_sex.columns = ['Count', 'Mean', 'Std Dev', 'Min', 'Median', 'Max']
    st.dataframe(stats_by_sex, use_container_width=True)

    # Statistical test (t-test)
    t_stat, p_value, n_male, n_female = ttest_for_groups(df_processed, selected_var)

    if not pd.isna(t_stat):
        st.subheader("Statistical Test (Welch's t-test)")
        stat_col1, stat_col2, stat_col3 = st.columns(3)

        with stat_col1:
            st.metric("t-statistic", f"{t_stat:.4f}")
        with stat_col2:
            st.metric("p-value", f"{p_value:.4f}")
        with stat_col3:
            significance = "Significant" if p_value < 0.05 else "Not Significant"
            st.metric("Result (α=0.05)", significance)

        if p_value < 0.05:
            st.success(f"Significant difference found (p={p_value:.4f} < 0.05)")
        else:
            st.info(f"No significant difference (p={p_value:.4f} >= 0.05)")
    else:
        st.warning(
            f"Not enough non-missing values for a t-test on {selected_var}. "
            f"Male n={n_male}, Female n={n_female}."
        )

st.divider()

# Multi-variable comparison
st.subheader("Multi-Variable Sex Comparison")

if len(numeric_cols) > 0:
    selected_vars = st.multiselect(
        "Select variables to compare",
        numeric_cols,
        default=numeric_cols[:min(3, len(numeric_cols))]
    )

    if selected_vars:
        # Mean comparison bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        male_means = df_processed[df_processed['Sex'] == 'Male'][selected_vars].mean()
        female_means = df_processed[df_processed['Sex'] == 'Female'][selected_vars].mean()

        x = np.arange(len(selected_vars))
        width = 0.35

        bars1 = ax.bar(x - width/2, male_means, width, label='Male', color='#3498db', edgecolor='black')
        bars2 = ax.bar(x + width/2, female_means, width, label='Female', color='#e74c3c', edgecolor='black')

        ax.set_xlabel('Variables')
        ax.set_ylabel('Mean Value')
        ax.set_title('Mean Comparison by Sex')
        ax.set_xticks(x)
        ax.set_xticklabels(selected_vars, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()
        render_branded_figure(fig)
        plt.close()

        # Summary table
        summary_rows = []
        for var in selected_vars:
            male_vals = df_processed[df_processed['Sex'] == 'Male'][var].dropna()
            female_vals = df_processed[df_processed['Sex'] == 'Female'][var].dropna()
            male_mean = male_vals.mean()
            female_mean = female_vals.mean()
            t_stat, p_value, n_male, n_female = ttest_for_groups(df_processed, var)

            summary_rows.append({
                'Variable': var,
                'Male Mean': male_mean,
                'Female Mean': female_mean,
                'Difference': male_mean - female_mean,
                'Diff %': safe_percent_diff(male_mean, female_mean),
                'Male n': n_male,
                'Female n': n_female,
                't-stat': t_stat,
                'p-value': p_value,
                'Significance (alpha=0.05)': pvalue_to_label(p_value)
            })

        comparison_df = pd.DataFrame({
            'Variable': [row['Variable'] for row in summary_rows],
            'Male Mean': [row['Male Mean'] for row in summary_rows],
            'Female Mean': [row['Female Mean'] for row in summary_rows],
            'Difference': [row['Difference'] for row in summary_rows],
            'Diff %': [row['Diff %'] for row in summary_rows],
            'Male n': [row['Male n'] for row in summary_rows],
            'Female n': [row['Female n'] for row in summary_rows],
            't-stat': [row['t-stat'] for row in summary_rows],
            'p-value': [row['p-value'] for row in summary_rows],
            'Significance (alpha=0.05)': [row['Significance (alpha=0.05)'] for row in summary_rows],
        }).round(4)
        st.dataframe(comparison_df, use_container_width=True)

        # Effect size analysis
        st.subheader("Effect Size Analysis (Cohen's d)")
        effect_col1, effect_col2 = st.columns(2)
        
        with effect_col1:
            effect_var = st.selectbox("Select variable for effect size", selected_vars, key="effect_size")
        
        with effect_col2:
            st.write("")
            st.write("")
            if st.button("Calculate Cohen's d", use_container_width=True):
                male_data = df_processed[df_processed['Sex'] == 'Male'][effect_var].dropna()
                female_data = df_processed[df_processed['Sex'] == 'Female'][effect_var].dropna()
                
                if len(male_data) > 1 and len(female_data) > 1:
                    cohens_d = effect_size_cohens_d(male_data, female_data)
                    if not pd.isna(cohens_d):
                        st.metric("Cohen's d", f"{cohens_d:.4f}")
                        if abs(cohens_d) < 0.2:
                            effect_label = "Negligible"
                        elif abs(cohens_d) < 0.5:
                            effect_label = "Small"
                        elif abs(cohens_d) < 0.8:
                            effect_label = "Medium"
                        else:
                            effect_label = "Large"
                        st.info(f"Effect Size: {effect_label}")
                    else:
                        st.warning("Cannot calculate Cohen's d with this data")
                else:
                    st.warning("Insufficient data for effect size calculation")
