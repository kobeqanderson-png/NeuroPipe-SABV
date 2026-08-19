#!/usr/bin/env python3
"""Stress tests for NeuroPipe-SABV with large datasets and edge cases."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.data_load import read_csv
from src.cleaning import basic_clean
from src.features import (
    add_log_feature,
    add_polynomial_features,
    add_interaction_features,
    standardize_features,
    add_missing_indicators
)

import re
from scipy import stats as scipy_stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def parse_animal_number(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip()
    if not text:
        return np.nan
    lower_text = text.lower()
    prefixed_match = re.search(r"(?:rat|subject|animal)\s*[-_#:]?\s*(\d+(?:\.\d+)?)", lower_text)
    if prefixed_match:
        return float(prefixed_match.group(1))
    numeric_only_match = re.fullmatch(r"\d+(?:\.\d+)?", lower_text)
    if numeric_only_match:
        return float(numeric_only_match.group(0))
    match = re.search(r"\d+(?:\.\d+)?", text)
    if match:
        return float(match.group(0))
    return np.nan

def parse_animal_number_series(series):
    return series.apply(parse_animal_number)

# ============================================================================
# STRESS TEST SUITE
# ============================================================================

print("=" * 80)
print("STRESS TEST SUITE - LARGE DATASETS & EDGE CASES")
print("=" * 80)

stress_results = []

def log_stress_test(test_num, test_name, status, exec_time, details=""):
    result = {
        "Test": test_num,
        "Name": test_name,
        "Status": status,
        "Time (s)": f"{exec_time:.3f}",
        "Details": details
    }
    stress_results.append(result)
    status_icon = "✓" if status == "PASS" else "✗"
    print(f"{status_icon} Stress {test_num}: {test_name}")
    print(f"   Duration: {exec_time:.3f}s | {details}\n")


# Stress Test 1: Large dataset (10,000 rows)
print("Running Stress Test 1: Large dataset (10,000 rows)...")
try:
    start = time.time()
    np.random.seed(42)
    df_large = pd.DataFrame({
        'Animal_ID': np.repeat(range(1, 5001), 2),
        'Weight': np.random.normal(25, 5, 10000),
        'Length': np.random.normal(20, 3, 10000),
        'Velocity': np.abs(np.random.normal(10, 2, 10000)),
        'Score1': np.random.uniform(0, 100, 10000),
        'Score2': np.random.uniform(0, 100, 10000),
    })
    exec_time = time.time() - start
    log_stress_test(1, "Create 10K row dataset", "PASS", exec_time, "10,000 rows × 6 cols")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(1, "Create 10K row dataset", "FAIL", exec_time, str(e)[:50])

# Stress Test 2: Process large dataset
print("Running Stress Test 2: Process 10K row dataset...")
try:
    start = time.time()
    df_large_clean = basic_clean(df_large.copy())
    exec_time = time.time() - start
    log_stress_test(2, "Clean 10K row dataset", "PASS", exec_time, f"{len(df_large_clean)} rows after cleaning")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(2, "Clean 10K row dataset", "FAIL", exec_time, str(e)[:50])

# Stress Test 3: Sex classification on large dataset
print("Running Stress Test 3: Sex classification (10K rows)...")
try:
    start = time.time()
    animal_nums = parse_animal_number_series(df_large_clean['Animal_ID'])
    sex_class = np.where(animal_nums <= 16, 'Male', 'Female')
    df_large_clean['Sex'] = sex_class
    exec_time = time.time() - start
    male_count = (df_large_clean['Sex'] == 'Male').sum()
    female_count = (df_large_clean['Sex'] == 'Female').sum()
    log_stress_test(3, "Sex classification (10K rows)", "PASS", exec_time, f"M={male_count}, F={female_count}")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(3, "Sex classification (10K rows)", "FAIL", exec_time, str(e)[:50])

# Stress Test 4: Feature engineering on large dataset
print("Running Stress Test 4: Full feature engineering pipeline (10K rows)...")
try:
    start = time.time()
    df_feat = df_large_clean.copy()
    df_feat = add_log_feature(df_feat, 'Weight')
    df_feat = add_polynomial_features(df_feat, 'Length', degree=3)
    df_feat = add_interaction_features(df_feat, 'Weight', 'Length')
    df_feat = standardize_features(df_feat, ['Weight', 'Length', 'Velocity'])
    df_feat = add_missing_indicators(df_feat, ['Weight', 'Length'])
    exec_time = time.time() - start
    log_stress_test(4, "Feature engineering pipeline (10K)", "PASS", exec_time, 
                   f"{len(df_feat.columns)} total columns created")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(4, "Feature engineering pipeline (10K)", "FAIL", exec_time, str(e)[:50])

# Stress Test 5: T-test on large dataset
print("Running Stress Test 5: T-test analysis (10K rows)...")
try:
    start = time.time()
    male_data = df_large_clean[df_large_clean['Sex'] == 'Male']['Weight'].dropna()
    female_data = df_large_clean[df_large_clean['Sex'] == 'Female']['Weight'].dropna()
    t_stat, p_val = scipy_stats.ttest_ind(male_data, female_data, equal_var=False)
    exec_time = time.time() - start
    log_stress_test(5, "T-test (10K rows, 2 groups)", "PASS", exec_time, 
                   f"p={p_val:.4f}, n1={len(male_data)}, n2={len(female_data)}")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(5, "T-test (10K rows)", "FAIL", exec_time, str(e)[:50])

# Stress Test 6: Linear regression (10K rows)
print("Running Stress Test 6: Linear regression (10K rows)...")
try:
    start = time.time()
    X = df_large_clean[['Weight', 'Length', 'Velocity']].dropna()
    y = df_large_clean.loc[X.index, 'Score1'].dropna()
    X = X.loc[y.index]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    r2 = model.score(X_test, y_test)
    exec_time = time.time() - start
    log_stress_test(6, "Linear regression (10K rows)", "PASS", exec_time, 
                   f"R²={r2:.4f}, train={len(X_train)}, test={len(X_test)}")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(6, "Linear regression (10K rows)", "FAIL", exec_time, str(e)[:50])

# Stress Test 7: Polynomial regression (10K rows, degree 3)
print("Running Stress Test 7: Polynomial regression (10K rows, degree 3)...")
try:
    start = time.time()
    X = df_large_clean[['Weight']].copy()
    X['Weight_pow2'] = X['Weight'] ** 2
    X['Weight_pow3'] = X['Weight'] ** 3
    y = df_large_clean['Score1']
    
    X_clean = X.dropna()
    y_clean = y.loc[X_clean.index].dropna()
    X_clean = X_clean.loc[y_clean.index]
    
    X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    r2 = model.score(X_test, y_test)
    exec_time = time.time() - start
    log_stress_test(7, "Polynomial regression (10K, deg 3)", "PASS", exec_time, f"R²={r2:.4f}")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(7, "Polynomial regression (10K, deg 3)", "FAIL", exec_time, str(e)[:50])

# Stress Test 8: Handle dataset with 50% missing values
print("Running Stress Test 8: Dataset with 50% missing values...")
try:
    start = time.time()
    df_missing = df_large.head(1000).copy()
    mask = np.random.random(df_missing.shape) < 0.5
    df_missing[mask] = np.nan
    
    df_missing_clean = basic_clean(df_missing.copy())
    exec_time = time.time() - start
    
    original_size = len(df_missing)
    cleaned_size = len(df_missing_clean)
    log_stress_test(8, "Handle 50% missing data", "PASS", exec_time, 
                   f"{original_size} → {cleaned_size} rows (lost {original_size - cleaned_size})")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(8, "Handle 50% missing data", "FAIL", exec_time, str(e)[:50])

# Stress Test 9: Extreme values (very large numbers)
print("Running Stress Test 9: Handle extreme values...")
try:
    start = time.time()
    df_extreme = df_large.head(1000).copy()
    df_extreme.loc[0, 'Weight'] = 1e10
    df_extreme.loc[1, 'Length'] = -1e10
    df_extreme.loc[2, 'Velocity'] = 0.0
    
    df_extreme_clean = basic_clean(df_extreme.copy())
    log_feat = add_log_feature(df_extreme_clean.copy(), 'Weight')
    exec_time = time.time() - start
    log_stress_test(9, "Handle extreme values", "PASS", exec_time, "Very large/small/zero values handled")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(9, "Handle extreme values", "FAIL", exec_time, str(e)[:50])

# Stress Test 10: Single column dataset
print("Running Stress Test 10: Minimal dataset (single numeric column)...")
try:
    start = time.time()
    df_minimal = pd.DataFrame({
        'Animal_ID': range(1, 51),
        'Value': np.random.normal(50, 10, 50)
    })
    df_min_clean = basic_clean(df_minimal)
    animal_nums = parse_animal_number_series(df_min_clean['Animal_ID'])
    df_min_clean['Sex'] = np.where(animal_nums <= 16, 'Male', 'Female')
    log_feat = add_log_feature(df_min_clean.copy(), 'Value')
    exec_time = time.time() - start
    log_stress_test(10, "Minimal dataset (1 numeric col)", "PASS", exec_time, "Processed successfully")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(10, "Minimal dataset (1 numeric col)", "FAIL", exec_time, str(e)[:50])

# Stress Test 11: Mixed data types
print("Running Stress Test 11: Mixed data types (numeric + string + categorical)...")
try:
    start = time.time()
    df_mixed = pd.DataFrame({
        'Animal_ID': [f'rat_{i}' for i in range(1, 1001)],
        'Weight': np.random.normal(25, 5, 1000),
        'Category': np.random.choice(['A', 'B', 'C'], 1000),
        'Notes': ['observation_' + str(i) for i in range(1000)],
    })
    df_mixed_clean = basic_clean(df_mixed)
    animal_nums = parse_animal_number_series(df_mixed_clean['Animal_ID'])
    df_mixed_clean['Sex'] = np.where(animal_nums <= 16, 'Male', 'Female')
    exec_time = time.time() - start
    log_stress_test(11, "Mixed data types (1K rows)", "PASS", exec_time, 
                   f"Handled numeric + string + categorical")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(11, "Mixed data types (1K rows)", "FAIL", exec_time, str(e)[:50])

# Stress Test 12: Many columns (100 features)
print("Running Stress Test 12: High dimensionality (100 numeric columns)...")
try:
    start = time.time()
    df_wide = pd.DataFrame({
        'Animal_ID': range(1, 101),
        **{f'Feature_{i}': np.random.normal(0, 1, 100) for i in range(100)}
    })
    df_wide_clean = basic_clean(df_wide)
    animal_nums = parse_animal_number_series(df_wide_clean['Animal_ID'])
    df_wide_clean['Sex'] = np.where(animal_nums <= 16, 'Male', 'Female')
    exec_time = time.time() - start
    log_stress_test(12, "High dimensionality (100 cols)", "PASS", exec_time, f"{len(df_wide_clean.columns)} total columns")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(12, "High dimensionality (100 cols)", "FAIL", exec_time, str(e)[:50])

# Stress Test 13: Imbalanced sex distribution
print("Running Stress Test 13: Imbalanced sex distribution (95/5 split)...")
try:
    start = time.time()
    animal_ids = list(range(1, 51)) + list(range(101, 1001))  # 50 male + 900 female = 950 total
    df_imbalanced = pd.DataFrame({
        'Animal_ID': animal_ids,
        'Weight': np.random.normal(25, 5, len(animal_ids)),
    })
    df_imb_clean = basic_clean(df_imbalanced)
    animal_nums = parse_animal_number_series(df_imb_clean['Animal_ID'])
    df_imb_clean['Sex'] = np.where(animal_nums <= 16, 'Male', 'Female')
    
    male_count = (df_imb_clean['Sex'] == 'Male').sum()
    female_count = (df_imb_clean['Sex'] == 'Female').sum()
    ratio = male_count / female_count if female_count > 0 else 0
    
    male_data = df_imb_clean[df_imb_clean['Sex'] == 'Male']['Weight'].dropna()
    female_data = df_imb_clean[df_imb_clean['Sex'] == 'Female']['Weight'].dropna()
    if len(male_data) > 1 and len(female_data) > 1:
        t_stat, p_val = scipy_stats.ttest_ind(male_data, female_data, equal_var=False)
    
    exec_time = time.time() - start
    log_stress_test(13, "Imbalanced data (95/5)", "PASS", exec_time, 
                   f"M={male_count}, F={female_count}, ratio={ratio:.3f}")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(13, "Imbalanced data (95/5)", "FAIL", exec_time, str(e)[:50])

# Stress Test 14: All same values (zero variance)
print("Running Stress Test 14: Zero variance column...")
try:
    start = time.time()
    df_zero_var = pd.DataFrame({
        'Animal_ID': range(1, 101),
        'Weight': np.ones(100) * 25.0,  # All same value
        'Length': np.random.normal(20, 3, 100),
    })
    df_zv_clean = basic_clean(df_zero_var)
    std_weight = df_zv_clean['Weight'].std()
    log_feat = add_polynomial_features(df_zv_clean.copy(), 'Weight')
    std_feat = standardize_features(df_zv_clean.copy(), ['Weight'])
    exec_time = time.time() - start
    log_stress_test(14, "Zero variance column", "PASS", exec_time, 
                   f"Std(Weight)={std_weight:.6f}, handled gracefully")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(14, "Zero variance column", "FAIL", exec_time, str(e)[:50])

# Stress Test 15: Very unbalanced feature interactions
print("Running Stress Test 15: Extreme range feature interaction...")
try:
    start = time.time()
    df_extreme_range = pd.DataFrame({
        'Animal_ID': range(1, 501),
        'Feature_A': np.random.exponential(1, 500),  # 0-20 range roughly
        'Feature_B': np.random.uniform(1e6, 1e7, 500),  # Very large range
    })
    df_er_clean = basic_clean(df_extreme_range)
    df_interact = add_interaction_features(df_er_clean.copy(), 'Feature_A', 'Feature_B')
    df_stand = standardize_features(df_interact.copy(), ['Feature_A', 'Feature_B', 'Feature_A_x_Feature_B'])
    exec_time = time.time() - start
    log_stress_test(15, "Extreme-range interaction", "PASS", exec_time, "Different scale features handled")
except Exception as e:
    exec_time = time.time() - start
    log_stress_test(15, "Extreme-range interaction", "FAIL", exec_time, str(e)[:50])

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("STRESS TEST SUMMARY")
print("=" * 80)

df_stress = pd.DataFrame(stress_results)
pass_count = (df_stress['Status'] == 'PASS').sum()
fail_count = (df_stress['Status'] == 'FAIL').sum()
total_time = sum([float(t.replace('s', '')) for t in df_stress['Time (s)']])

print(f"\nTotal Stress Tests: {len(df_stress)}")
print(f"Passed: {pass_count} ✓")
print(f"Failed: {fail_count} ✗")
print(f"Total Execution Time: {total_time:.2f}s")
print(f"Average Time per Test: {total_time/len(df_stress):.3f}s")

if fail_count == 0:
    print("\n🎉 ALL STRESS TESTS PASSED!")
    print("\nPipeline Performance Summary:")
    print("  • Handles 10,000+ row datasets efficiently")
    print("  • Robust feature engineering with multiple transformations")
    print("  • Gracefully handles missing values and extreme data")
    print("  • Works with high-dimensional data (100+ columns)")
    print("  • Handles imbalanced group designs")
    print("  • Manages edge cases (zero variance, extreme ranges)")
else:
    print(f"\n⚠  {fail_count} test(s) failed")

print("\n" + "=" * 80)
