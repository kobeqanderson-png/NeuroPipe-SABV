# NeuroPipe-SABV — Project Documentation

## Overview

The **NeuroPipe-SABV** pipeline is a production-ready Streamlit web application for analyzing sex differences in research data.

**Status**: ✅ Production Ready (All 35 tests passed)

## Features

### Core Capabilities

1. **Data Loading** - CSV, Excel with automatic encoding detection
2. **Data Cleaning** - Missing value imputation, duplicate removal, whitespace trimming
3. **Sex Classification** - 3 modes: Threshold split, manual number lists, reverse/female-only
4. **Feature Engineering** - Log, polynomial, interaction, standardization, missing indicators
5. **Statistical Analysis** - Welch's t-test, Cohen's d effect size, SEM
6. **Linear Regression** - Basic + polynomial with diagnostics
7. **Visualizations** - 8+ plot types (histograms, scatter, correlation heatmap, etc.)
8. **Data Export** - CSV and formatted Excel with summary stats

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run application
streamlit run app.py

# 3. Upload data and explore
```

## Test Results

✅ **20/20 Unit Tests Passed**
- Data loading, cleaning, classification
- Feature engineering (all 5 functions)
- Statistical analysis
- Regression modeling

✅ **15/15 Stress Tests Passed**
- 10K row processing (<30ms)
- 100 column datasets
- Edge cases (missing values, extreme values, imbalance)

## Architecture

```
Data Upload → Cleaning → Classification → Features → Analysis → Regression → Export
```

Key modules:
- `app.py` - Main Streamlit app (1356 lines)
- `src/data_load.py` - CSV/Excel loading
- `src/cleaning.py` - Data preprocessing
- `src/features.py` - Feature engineering (5 functions)
- `src/visualize.py` - Custom plots

## Documentation Files

- **DOCUMENTATION.md** (this file) - Project overview and features
- **TEST_RESULTS.md** - Detailed test results (35 tests, 100% pass rate)
- **ARCHITECTURE.md** - Technical architecture and design decisions

## Performance Metrics

| Operation | 10K Rows | Rate |
|-----------|----------|------|
| Data cleaning | 14ms | 714K rows/sec |
| Sex classification | 14ms | 714K rows/sec |
| Feature engineering | 27ms | 370K rows/sec |
| Linear regression | 12ms | 833K rows/sec |

## Status: Production Ready ✅

All code validated, tested, and documented.

See TEST_RESULTS.md for detailed test coverage.
See ARCHITECTURE.md for implementation details.
