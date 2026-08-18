"""Pytest suite for NIH SABV data processing pipeline.

Run with:
    pytest test_pipeline.py -v
"""

import sys
from pathlib import Path
import io

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scipy_stats

# Ensure src is importable
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_load import read_csv, read_excel
from src.cleaning import basic_clean
from src.features import (
    add_log_feature,
    add_missing_indicators,
    add_polynomial_features,
    add_interaction_features,
    standardize_features,
)
from src.visualize import boxplot_by_category


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_df():
    """Standard 50-row synthetic dataset."""
    np.random.seed(42)
    return pd.DataFrame({
        "Animal_ID": range(1, 51),
        "Weight": np.random.normal(25, 5, 50),
        "Length": np.random.normal(20, 3, 50),
        "Velocity": np.abs(np.random.normal(10, 2, 50)),
    })


@pytest.fixture
def classified_df(synthetic_df):
    """Synthetic dataset with Sex column (threshold=16)."""
    df = synthetic_df.copy()
    df["Sex"] = np.where(df["Animal_ID"] <= 16, "Male", "Female")
    return df


# ---------------------------------------------------------------------------
# Helper functions (mirroring app logic without Streamlit dependency)
# ---------------------------------------------------------------------------

def parse_animal_number(value):
    """Extract numeric animal ID from mixed formats."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip()
    if not text:
        return np.nan
    lower_text = text.lower()
    prefixed_match = __import__("re").search(
        r"(?:rat|subject|animal)\s*[-_#:]?\s*(\d+(?:\.\d+)?)",
        lower_text,
    )
    if prefixed_match:
        return float(prefixed_match.group(1))
    numeric_only_match = __import__("re").fullmatch(r"\d+(?:\.\d+)?", lower_text)
    if numeric_only_match:
        return float(numeric_only_match.group(0))
    match = __import__("re").search(r"\d+(?:\.\d+)?", text)
    if match:
        return float(match.group(0))
    return np.nan


def parse_animal_number_series(series):
    return series.apply(parse_animal_number)


def parse_id_list(raw_text):
    """Parse comma-separated IDs/ranges into a set of floats."""
    values = set()
    invalid_tokens = []
    for token in raw_text.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            parts = token.split("-", 1)
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
                start_i, end_i = int(start), int(end)
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


def ttest_for_groups(df, value_col, group_col="Sex"):
    male_data = df[df[group_col] == "Male"][value_col].dropna()
    female_data = df[df[group_col] == "Female"][value_col].dropna()
    if len(male_data) > 1 and len(female_data) > 1:
        t_stat, p_value = scipy_stats.ttest_ind(
            male_data, female_data, equal_var=False
        )
        return t_stat, p_value, len(male_data), len(female_data)
    return np.nan, np.nan, len(male_data), len(female_data)


def effect_size_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    if n1 < 2 or n2 < 2:
        return np.nan
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return np.nan
    return (group1.mean() - group2.mean()) / pooled_std


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class TestDataLoad:
    def test_read_csv_utf8(self):
        csv_bytes = b"A,B\n1,2\n3,4"
        df = read_csv(io.BytesIO(csv_bytes))
        assert df.shape == (2, 2)
        assert list(df.columns) == ["A", "B"]

    def test_read_csv_latin1_fallback(self):
        csv_bytes = "A,B\n1, café\n3,4".encode("latin1")
        df = read_csv(io.BytesIO(csv_bytes))
        assert df.shape == (2, 2)
        assert "café" in df.iloc[1, 1]

    def test_read_csv_unsupported_encoding_raises(self):
        csv_bytes = b"\xff\xfe invalid"
        with pytest.raises(ValueError, match="Could not decode CSV"):
            read_csv(io.BytesIO(csv_bytes))


# ---------------------------------------------------------------------------
# Data cleaning
# ---------------------------------------------------------------------------

class TestCleaning:
    def test_basic_clean_preserves_shape_with_no_issues(self, synthetic_df):
        df_clean = basic_clean(synthetic_df.copy())
        assert len(df_clean) == len(synthetic_df)
        assert len(df_clean.columns) >= len(synthetic_df.columns)

    def test_basic_clean_drops_duplicates(self, synthetic_df):
        df_dup = pd.concat([synthetic_df, synthetic_df.iloc[[0]]], ignore_index=True)
        df_clean = basic_clean(df_dup)
        assert len(df_clean) == len(synthetic_df)

    def test_basic_clean_fills_numeric_nans(self):
        df = pd.DataFrame({"A": [1.0, np.nan, 3.0], "B": ["x", "y", "z"]})
        df_clean = basic_clean(df)
        assert df_clean["A"].isna().sum() == 0
        # median of [1.0, 3.0] is 2.0
        assert df_clean.loc[1, "A"] == pytest.approx(2.0)

    def test_basic_clean_strips_column_names(self):
        df = pd.DataFrame({"  Col A  ": [1, 2], "B ": [3, 4]})
        df_clean = basic_clean(df)
        assert "Col A" in df_clean.columns
        assert "B" in df_clean.columns

    def test_basic_clean_drops_rows_missing_required_ids(self):
        df = pd.DataFrame({"ID": [1, np.nan, 3], "Val": [10, 20, 30]})
        df_clean = basic_clean(df, id_cols=["ID"])
        assert len(df_clean) == 2
        assert 2 not in df_clean.index


# ---------------------------------------------------------------------------
# Animal ID parsing
# ---------------------------------------------------------------------------

class TestAnimalIDParsing:
    @pytest.mark.parametrize(
        "input_val,expected",
        [
            (1, 1.0),
            (1.5, 1.5),
            ("rat17", 17.0),
            ("subject_5", 5.0),
            ("animal-123", 123.0),
            ("42", 42.0),
            ("mixed_text_99_here", 99.0),
            ("", np.nan),
            (np.nan, np.nan),
        ],
    )
    def test_parse_animal_number(self, input_val, expected):
        result = parse_animal_number(input_val)
        if np.isnan(expected):
            assert np.isnan(result)
        else:
            assert result == pytest.approx(expected)

    def test_parse_animal_number_series(self, synthetic_df):
        nums = parse_animal_number_series(synthetic_df["Animal_ID"])
        assert nums.notna().sum() == 50
        assert nums.iloc[0] == 1.0


# ---------------------------------------------------------------------------
# ID list parsing
# ---------------------------------------------------------------------------

class TestIDListParsing:
    def test_parse_id_list_basic_range(self):
        ids, invalid = parse_id_list("1-16, 20")
        assert len(ids) == 17
        assert 1.0 in ids
        assert 16.0 in ids
        assert 20.0 in ids
        assert len(invalid) == 0

    def test_parse_id_list_overlap_detection(self):
        male_ids, _ = parse_id_list("1-10")
        female_ids, _ = parse_id_list("8-15")
        overlap = male_ids.intersection(female_ids)
        assert overlap == {8.0, 9.0, 10.0}

    def test_parse_id_list_invalid_tokens(self):
        ids, invalid = parse_id_list("1-10, abc, 20-xyz")
        assert "abc" in invalid
        assert "20-xyz" in invalid
        assert 1.0 in ids

    def test_parse_id_list_reversed_range(self):
        ids, invalid = parse_id_list("10-5")
        assert len(ids) == 6
        assert 5.0 in ids
        assert 10.0 in ids


# ---------------------------------------------------------------------------
# Sex classification
# ---------------------------------------------------------------------------

class TestSexClassification:
    def test_threshold_classification(self, synthetic_df):
        nums = parse_animal_number_series(synthetic_df["Animal_ID"])
        sex = np.where(
            nums <= 16, "Male", np.where(nums > 16, "Female", "Unclassified")
        )
        assert (sex == "Male").sum() == 16
        assert (sex == "Female").sum() == 34

    def test_manual_list_classification(self, synthetic_df):
        nums = parse_animal_number_series(synthetic_df["Animal_ID"])
        male_ids, _ = parse_id_list("1-16")
        female_ids, _ = parse_id_list("17-50")
        sex = np.select(
            [nums.isin(male_ids), nums.isin(female_ids)],
            ["Male", "Female"],
            default="Unclassified",
        )
        assert (sex == "Male").sum() == 16
        assert (sex == "Female").sum() == 34

    def test_classification_mode_equivalence(self, synthetic_df):
        nums = parse_animal_number_series(synthetic_df["Animal_ID"])
        threshold_sex = np.where(nums <= 16, "Male", "Female")
        manual_ids, _ = parse_id_list("1-16")
        manual_sex = np.where(nums.isin(manual_ids), "Male", "Female")
        assert (threshold_sex == manual_sex).all()

    def test_unclassified_for_non_numeric(self):
        df = pd.DataFrame({"Animal_ID": ["rat", "subject", "42"]})
        nums = parse_animal_number_series(df["Animal_ID"])
        assert nums.isna().sum() == 2


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

class TestStatistics:
    def test_ttest_returns_valid_numbers(self, classified_df):
        t_stat, p_value, n_m, n_f = ttest_for_groups(classified_df, "Weight")
        assert not np.isnan(t_stat)
        assert not np.isnan(p_value)
        assert n_m == 16
        assert n_f == 34

    def test_ttest_small_sample_returns_nan(self):
        df = pd.DataFrame({
            "Sex": ["Male", "Male", "Female"],
            "Val": [1.0, 2.0, 3.0],
        })
        t_stat, p_value, n_m, n_f = ttest_for_groups(df, "Val")
        assert np.isnan(t_stat)
        assert np.isnan(p_value)

    def test_cohens_d_reasonable_range(self, classified_df):
        male_w = classified_df[classified_df["Sex"] == "Male"]["Weight"].dropna()
        female_w = classified_df[classified_df["Sex"] == "Female"]["Weight"].dropna()
        d = effect_size_cohens_d(male_w, female_w)
        assert not np.isnan(d)
        assert abs(d) < 5  # Sanity bound for random data

    def test_cohens_d_insufficient_data(self):
        g1 = pd.Series([1.0])
        g2 = pd.Series([2.0, 3.0])
        d = effect_size_cohens_d(g1, g2)
        assert np.isnan(d)

    def test_cohens_d_zero_variance(self):
        g1 = pd.Series([5.0, 5.0, 5.0])
        g2 = pd.Series([3.0, 4.0, 5.0])
        d = effect_size_cohens_d(g1, g2)
        assert np.isnan(d)


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

class TestFeatureEngineering:
    def test_add_log_feature(self, synthetic_df):
        df = add_log_feature(synthetic_df.copy(), "Weight")
        assert "Weight_log" in df.columns
        assert df["Weight_log"].notna().sum() > 0

    def test_add_polynomial_features(self, synthetic_df):
        df = add_polynomial_features(synthetic_df.copy(), "Weight", degree=3)
        assert "Weight_pow2" in df.columns
        assert "Weight_pow3" in df.columns

    def test_add_interaction_features(self, synthetic_df):
        df = add_interaction_features(synthetic_df.copy(), "Weight", "Length")
        assert "Weight_x_Length" in df.columns

    def test_standardize_features(self, synthetic_df):
        df = standardize_features(synthetic_df.copy(), ["Weight", "Length"])
        assert "Weight_std" in df.columns
        assert "Length_std" in df.columns
        assert abs(df["Weight_std"].mean()) < 0.01
        assert abs(df["Weight_std"].std() - 1.0) < 0.01

    def test_standardize_zero_variance(self):
        df = pd.DataFrame({"A": [5.0, 5.0, 5.0], "B": [1.0, 2.0, 3.0]})
        df_std = standardize_features(df.copy(), ["A", "B"])
        assert (df_std["A_std"] == 0).all()
        assert df_std["B_std"].std() == pytest.approx(1.0, abs=0.01)

    def test_add_missing_indicators(self, synthetic_df):
        df = synthetic_df.copy()
        df.loc[0:2, "Weight"] = np.nan
        df = add_missing_indicators(df, ["Weight", "Length"])
        assert "Weight_missing" in df.columns
        assert "Length_missing" in df.columns
        assert df.loc[0, "Weight_missing"] == 1
        assert df.loc[0, "Length_missing"] == 0

    def test_full_feature_pipeline(self, synthetic_df):
        df = synthetic_df.copy()
        df = add_log_feature(df, "Weight")
        df = add_polynomial_features(df, "Length", degree=2)
        df = add_interaction_features(df, "Weight", "Length")
        df = standardize_features(df, ["Weight", "Length"])
        df = add_missing_indicators(df, ["Weight", "Length"])
        expected = [
            "Weight_log",
            "Length_pow2",
            "Weight_x_Length",
            "Weight_std",
            "Length_std",
            "Weight_missing",
            "Length_missing",
        ]
        for col in expected:
            assert col in df.columns


# ---------------------------------------------------------------------------
# Regression / sklearn integration
# ---------------------------------------------------------------------------

class TestRegression:
    def test_linear_regression_runs(self, classified_df):
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split

        X = classified_df[["Weight", "Length"]].dropna()
        y = classified_df.loc[X.index, "Velocity"].dropna()
        X = X.loc[y.index]

        if len(X) > 5:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            model = LinearRegression()
            model.fit(X_train, y_train)
            r2 = model.score(X_test, y_test)
            assert isinstance(r2, (float, np.floating))

    def test_polynomial_regression_runs(self, classified_df):
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split

        X = classified_df[["Weight"]].copy()
        X["Weight_pow2"] = X["Weight"] ** 2
        y = classified_df["Velocity"]
        X_clean = X.dropna()
        y_clean = y.loc[X_clean.index].dropna()
        X_clean = X_clean.loc[y_clean.index]

        if len(X_clean) > 5:
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y_clean, test_size=0.2, random_state=42
            )
            model = LinearRegression()
            model.fit(X_train, y_train)
            r2 = model.score(X_test, y_test)
            assert isinstance(r2, (float, np.floating))

    def test_residual_analysis(self, classified_df):
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error

        X = classified_df[["Weight", "Length"]].dropna()
        y = classified_df.loc[X.index, "Velocity"].dropna()
        X = X.loc[y.index]

        if len(X) > 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            residuals = y_test - y_pred

            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            assert mae >= 0
            assert rmse >= 0
            assert len(residuals) == len(y_test)


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

class TestVisualization:
    def test_boxplot_by_category(self, classified_df):
        fig = boxplot_by_category(classified_df, "Weight", "Sex")
        assert fig is not None


# ---------------------------------------------------------------------------
# End-to-end integration
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_full_pipeline_no_errors(self, synthetic_df):
        """Simulate the core pipeline: load -> clean -> classify -> features -> stats."""
        df = basic_clean(synthetic_df.copy())
        nums = parse_animal_number_series(df["Animal_ID"])
        df["Sex"] = np.where(nums <= 16, "Male", "Female")
        df = add_log_feature(df, "Weight")
        df = standardize_features(df, ["Weight", "Length"])
        t_stat, p_value, n_m, n_f = ttest_for_groups(df, "Weight")
        assert not np.isnan(t_stat)
        assert n_m + n_f == len(df)
