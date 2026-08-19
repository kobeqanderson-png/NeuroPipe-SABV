# Architecture & Implementation Guide

**Project**: NeuroPipe-SABV  
**Version**: 1.0  
**Last Updated**: April 1, 2026

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB APPLICATION                 │
│                          (app.py)                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  1. DATA INGESTION LAYER                           │    │
│  │  - File upload (CSV, Excel)                        │    │
│  │  - Encoding detection (UTF-8, Latin-1, etc.)       │    │
│  │  - Column type inference                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  2. DATA PROCESSING LAYER                          │    │
│  │  src/cleaning.py  → basic_clean()                  │    │
│  │  - Missing value imputation                        │    │
│  │  - Duplicate removal                               │    │
│  │  - Whitespace trimming                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  3. SEX CLASSIFICATION LAYER                       │    │
│  │  app.py → parse_animal_number() + classification  │    │
│  │  - Threshold split                                 │    │
│  │  - Manual ID lists                                 │    │
│  │  - Reverse/Female-only mode                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  4. FEATURE ENGINEERING LAYER                      │    │
│  │  src/features.py → 5 transformation functions      │    │
│  │  - Log transformation                              │    │
│  │  - Polynomial features                             │    │
│  │  - Interaction terms                               │    │
│  │  - Standardization                                 │    │
│  │  - Missing indicators                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  5. ANALYSIS & VISUALIZATION LAYER                 │    │
│  │  src/visualize.py + matplotlib/seaborn             │    │
│  │  - Distribution plots                              │    │
│  │  - Statistical comparisons                         │    │
│  │  - Correlation analysis                            │    │
│  │  - Regression diagnostics                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  6. STATISTICAL ANALYSIS LAYER                     │    │
│  │  scipy.stats.ttest_ind() + custom effect size      │    │
│  │  - Welch's t-test                                  │    │
│  │  - Cohen's d effect size                           │    │
│  │  - SEM calculations                                │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  7. REGRESSION MODELING LAYER                      │    │
│  │  sklearn.linear_model.LinearRegression             │    │
│  │  - Feature selection                               │    │
│  │  - Train/test split (configurable %)               │    │
│  │  - Polynomial feature generation                   │    │
│  │  - Residual diagnostics                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                           ↓                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  8. EXPORT LAYER                                   │    │
│  │  pandas.to_csv() + openpyxl.Workbook()             │    │
│  │  - Formatted CSV export                            │    │
│  │  - Organized Excel with summary stats              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### 1. Main Application (`app.py` - 1356 lines)

**Purpose**: Orchestrate all components, manage UI state, render Streamlit interface

**Key Classes/Functions**:
- `apply_custom_theme()`: Injects dark mode CSS
- `parse_animal_number(value)`: Extract numeric ID from mixed formats
- `parse_animal_number_series(series)`: Vectorized parse
- `parse_id_list(raw_text)`: Parse ranges and comma-separated IDs
- `ttest_for_groups(df, value_col)`: Perform Welch's t-test
- `effect_size_cohens_d(group1, group2)`: Calculate Cohen's d
- `build_excel_export(df, animal_col, threshold)`: Format Excel output

**Dependencies**:
```python
streamlit, pandas, numpy, scipy, sklearn, matplotlib, seaborn, openpyxl, re
```

**Session State Keys**:
```python
df_raw              # Original uploaded data
df_processed        # After cleaning + classification
sex_col_used        # Column name used for sex classification
sex_threshold_used  # Threshold value (16 default)
sex_rebuild_from_threshold  # Mode flag for Excel export
```

---

### 2. Data Loading (`src/data_load.py`)

**Purpose**: Read CSV/Excel files with robust error handling

**Functions**:
```python
def read_csv(file_obj) → DataFrame
    # Multi-encoding fallback: UTF-8 → Latin-1 → ISO-8859-1
    
def read_excel(file_obj) → DataFrame
    # Returns first sheet

def save_clean(df, filepath) → None
    # Save cleaned data to CSV (unused in current app)
```

**Encoding Detection Strategy**:
```
1. Try UTF-8 (default)
2. Catch exception → Try Latin-1
3. Catch exception → Try ISO-8859-1
4. Catch exception → Raise error with helpful message
```

---

### 3. Data Cleaning (`src/cleaning.py`)

**Purpose**: Standardize data quality before analysis

**Functions**:
```python
def basic_clean(df: DataFrame) → DataFrame
    """
    Operations (in order):
    1. Fill numeric columns: median
    2. Fill categorical columns: mode
    3. Remove duplicate rows
    4. Strip whitespace from strings
    5. Return cleaned copy
    """
    
def save_clean(df, filepath) → None
    """Save to CSV (utility function)"""
```

**Implementation Details**:
- Uses `.fillna()` for imputation
- `.drop_duplicates()` for duplicate removal with `keep='first'`
- `.str.strip()` for whitespace (only on string columns)
- Returns fresh copy (doesn't modify original)

---

### 4. Feature Engineering (`src/features.py` - 90 lines)

**Purpose**: Create derived features for downstream analysis

**Functions**:

#### `add_log_feature(df, col, new_col=None) → DataFrame`
```python
# Log1p transform with handling for edges
- Clip negatives to 0 (add abs(min) if min < 0)
- Apply np.log1p() [log(1+x), better for small values]
- Create new column with name "{col}_log" (default)
```

#### `add_polynomial_features(df, col, degree=2) → DataFrame`
```python
# Create powers: x², x³, x⁴, etc.
- For each d in range(2, degree+1):
    - New column: "{col}_pow{d}" = col^d
```

#### `add_interaction_features(df, col1, col2) → DataFrame`
```python
# Cross-multiply two columns
- New column: "{col1}_x_{col2}" = col1 × col2
```

#### `standardize_features(df, cols) → DataFrame`
```python
# Z-score normalize (µ=0, σ=1)
- For each col:
    - mean = col.mean()
    - std = col.std()
    - If std > 0: (col - mean) / std
    - Else: 0 (for zero-variance columns)
    - New column: "{col}_std"
```

#### `add_missing_indicators(df, cols) → DataFrame`
```python
# Binary flags for missing values
- For each col:
    - New column: "{col}_missing" = 1 if NaN else 0
```

---

### 5. Visualization (`src/visualize.py`)

**Purpose**: Custom plotting utilities

**Functions**:
```python
def boxplot_by_category(df, numeric_col, category_col) → Figure
    # Create box plot grouped by category
    
def countplot(df, category_col) → Figure
    # Bar chart of category frequencies
```

**Note**: Main visualizations in app.py use matplotlib/seaborn directly

---

### 6. Configuration (`.streamlit/config.toml`)

**Purpose**: Streamlit native theme settings

```toml
[theme]
base = "dark"
primaryColor = "#22c55e"      # Green accent
backgroundColor = "#0d1117"    # Dark background
secondaryBackgroundColor = "#161b22"
textColor = "#d1d5db"
font = "monospace"
```

---

## Data Flow Examples

### Example 1: Complete Pipeline

```python
# User uploads CSV file "data.csv" with columns: Animal_ID, Weight, Length, Sex
# Animal_ID values: 1-50 (mixed)

# STEP 1: Load
uploaded_file = st.file_uploader(...)
df_raw = read_csv(uploaded_file)
# df_raw: 50 rows × 4 cols

# STEP 2: Clean
df_processed = basic_clean(df_raw)
# Removes duplicates, fills missing values
# df_processed: 49 rows × 4 cols (1 duplicate removed)

# STEP 3: Classify
sex_numeric = parse_animal_number_series(df_processed['Animal_ID'])
# sex_numeric: [1.0, 2.0, 3.0, ..., 50.0]

df_processed['Sex'] = np.where(
    sex_numeric <= 16,
    'Male',
    np.where(sex_numeric > 16, 'Female', 'Unclassified')
)
# df_processed now has Sex column: Male (1-16) vs Female (17-50)

# STEP 4: Feature Engineering (optional)
df_processed = add_log_feature(df_processed, 'Weight')
df_processed = add_polynomial_features(df_processed, 'Length', degree=2)
df_processed = standardize_features(df_processed, ['Weight', 'Length'])
# df_processed: 49 rows × 9 cols (added Weight_log, Length_pow2, Weight_std, Length_std)

# STEP 5: Statistical Analysis
male_weight = df_processed[df_processed['Sex']=='Male']['Weight'].dropna()
female_weight = df_processed[df_processed['Sex']=='Female']['Weight'].dropna()

t_stat, p_value = scipy_stats.ttest_ind(male_weight, female_weight, equal_var=False)
# t_stat = -1.234, p_value = 0.0456 (significant!)

cohens_d = effect_size_cohens_d(male_weight, female_weight)
# cohens_d = 0.567 (medium effect)

# STEP 6: Visualize
fig = plt.scatter(df_processed['Weight'], df_processed['Length'], 
                  c=[{'Male': 'blue', 'Female': 'red'}[s] 
                     for s in df_processed['Sex']])
# Renders scatter plot colored by sex

# STEP 7: Regression
X = df_processed[['Weight', 'Length']].dropna()
y = df_processed.loc[X.index, 'age']  # Hypothetical target

model = LinearRegression()
model.fit(X, y)
# Fitted model with coefficients

# STEP 8: Export
excel_bytes = build_excel_export(df_processed, animal_col='Animal_ID', threshold=16)
st.download_button("Download Excel", excel_bytes, "results.xlsx")
```

### Example 2: Manual Sex Classification

```python
# User mode: "Manual number lists"
# Male IDs input: "1-10, 15"
# Female IDs input: "11-14, 16-20"

male_ids, _ = parse_id_list("1-10, 15")
# male_ids = {1.0, 2.0, ..., 10.0, 15.0}

female_ids, _ = parse_id_list("11-14, 16-20")
# female_ids = {11.0, 12.0, 13.0, 14.0, 16.0, 17.0, 18.0, 19.0, 20.0}

# Check overlap
overlap = male_ids.intersection(female_ids)
# overlap = {} (empty, no conflict)

# Classify
df_processed['Sex'] = np.select(
    [sex_numeric.isin(male_ids), sex_numeric.isin(female_ids)],
    ['Male', 'Female'],
    default='Unclassified'
)
```

---

## Key Design Decisions

### 1. Why Welch's t-test?
- Doesn't assume equal variances (more conservative)
- Common in biological research
- Handles imbalanced group sizes

### 2. Why Cohen's d?
- Standardized effect size (unit-less)
- Complements p-values (practical vs statistical significance)
- Allows comparison across studies

### 3. Why parse_animal_number?
- Real data often has mixed formats: "rat17", "subject_5", "animal-123"
- Regex-based approach handles variety
- Vectorized with `.apply()` for efficiency

### 4. Why immediate Excel export with summary stats?
- Researchers expect formatted output
- Summary table with t-test results + SEM standard practice
- Animal-ordered view makes verification easier

### 5. Why monospace dark theme?
- NIH/scientific context → professional appearance
- Dark mode reduces eye strain for long analysis sessions
- Monospace improves numeric readability

---

## Error Handling Strategy

### Boundary Conditions

| Condition | Handler | Result |
|-----------|---------|--------|
| Empty file upload | st.error() + st.stop() | User sees error message |
| All-zero feature | std = 0 | Standardize returns 0 (no division) |
| Negative log input | Clip to 0 before log1p() | No complex numbers |
| No numeric columns | st.warning() | Skips visualization |
| Single-sample t-test | Return (NaN, NaN) | stat_col metric shows NaN |
| Overlapping ID lists | st.warning() with overlap list | Male takes precedence |
| Unclassified rows | st.warning() count | Shows how many rows unclassified |

### Exception Handling

```python
try:
    df_raw = read_csv(uploaded_file)
except UnicodeDecodeError:
    st.error("File encoding not supported")
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()
```

---

## Performance Optimization

### Current Bottlenecks

| Operation | Time (10K rows) | Optimization |
|-----------|-----------------|--------------|
| DataFrame creation | 5ms | NumPy efficient |
| Cleaning (impute+drop_dup) | 14ms | Optimized pandas ops |
| Sex classification | 14ms | Vectorized with numpy.where |
| Feature engineering | 27ms | Vectorized operations |
| Visualization rendering | 100-500ms | Matplotlib/seaborn |
| Correlation heatmap | 200-800ms | Limited to min(20, n_cols) |

### Caching Opportunities (Future)

```python
@st.cache_data
def load_and_clean(file_obj):
    return basic_clean(read_csv(file_obj))

@st.cache_data
def compute_correlation(df):
    return df.corr()  # Expensive for large dataframes
```

---

## Security Considerations

### Current Gaps
- ⚠️ No user authentication (anyone can access)
- ⚠️ No rate limiting (possibility of DOS)
- ⚠️ Files stored in memory (not persisted safely)
- ⚠️ No data encryption in transit/at rest

### Recommendations
- Deploy behind proxy with authentication
- Use environment variables for sensitive config
- Add timeout for large file processing
- Consider HTTPS-only Streamlit Cloud deployment

---

## Testing Architecture

### Test Organization

```
test_pipeline.py (290 lines)
├── Unit Tests 1-20
│   ├── Core functions (parse_animal_number, parse_id_list)
│   ├── Feature functions (add_log, polynomials, etc.)
│   ├── Statistical (t-test, Cohen's d)
│   └── Integration (full pipeline)
└── Utilities
    ├── parse_animal_number()
    ├── ttest_for_groups()
    └── effect_size_cohens_d()

stress_tests.py (330 lines)
├── Stress Tests 1-15
│   ├── Scale (10K rows, 100 cols)
│   ├── Data quality (50% missing, extreme values)
│   ├── Edge cases (zero variance, imbalance)
│   └── Performance (throughput, memory)
└── Result capture
    ├── Status (PASS/FAIL)
    ├── Duration
    └── Details
```

### Running Tests

```bash
# Unit tests
python3 test_pipeline.py

# Stress tests
python3 stress_tests.py

# Specific test file syntax check
python3 -m py_compile app.py src/features.py
```

---

## Deployment Checklist

- [ ] All tests passing (35/35)
- [ ] Code syntax validated
- [ ] Dependencies pinned in requirements.txt
- [ ] Secrets removed (.env files)
- [ ] Documentation complete
- [ ] Dark theme verified
- [ ] Export formats tested (CSV, Excel)
- [ ] Large file handling tested (10K+)
- [ ] Team review completed
- [ ] Deployment environment configured

---

## Future Enhancement Roadmap

| Feature | Complexity | Priority |
|---------|-----------|----------|
| ANOVA (3+ groups) | Medium | High |
| Non-parametric tests (Mann-Whitney) | Low | Medium |
| Logistic regression | Medium | Medium |
| Random forest modeling | High | Low |
| Categorical variable support | Medium | High |
| Batch processing (1M+ rows) | High | Low |
| User authentication | Medium | High |
| Data persistence (database) | High | Medium |
| API mode (programmatic access) | High | Low |
| Report generation (PDF) | Medium | Low |

---

**End of Architecture Document**
