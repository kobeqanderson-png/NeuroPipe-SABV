---
title: 'NeuroPipe-SABV: An NIH SABV-Compliant Data Processing Pipeline for Preclinical Behavioral Neuroscience'
tags:
  - Python
  - Streamlit
  - behavioral neuroscience
  - sex as a biological variable
  - SABV
  - data pipeline
  - preclinical
authors:
  - name: Kobe Q. Anderson
    orcid: 0009-0006-5464-1323
    affiliation: 1
  - name: Bryan Devan
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Laboratory for Comparative Neuropsychology, Department of Psychology, Towson University
    index: 1
date: 18 August 2026
bibliography: paper.bib
---

# Summary

Preclinical behavioral neuroscience labs routinely export messy, inconsistent CSV files from video-tracking platforms such as EthoVision XT and ANY-maze. Cleaning these exports, classifying subjects by sex, checking for artifacts, running statistics, and producing publication-ready figures is tedious, error-prone, and time-consuming, often taking hours per dataset. Additionally, the National Institutes of Health (NIH) now mandates that sex be included as a biological variable (SABV) in all federally funded research. Most laboratories handle SABV compliance manually and inconsistently, using lab-specific Excel templates or ad hoc scripts that are rarely documented or shared.

NeuroPipe-SABV is a free, open-source Streamlit web application that automates the entire workflow from raw export to SABV-compliant analysis. The pipeline standardizes headers across inconsistent export formats, classifies sex automatically from subject identifiers or metadata, detects common tracking artifacts, runs group-comparison and regression statistics, verifies group balance between sexes and conditions, and generates publication-ready visualizations with SABV-compliant reporting. All processing steps are documented, reproducible, and exportable. The application is deployed at https://data-analysis-sabv.streamlit.app/ and the source code is available at https://github.com/kobeqanderson-png/nihdatapipeline under the MIT license.

# Statement of Need

In 2014, the NIH announced a policy requiring that sex be included as a biological variable in all preclinical research designs, analyses, and reporting [@clayton2014; @mccullough2014; @sandberg2015]. The policy was codified in guide notice NOT-OD-15-102 and remains in effect today. Despite this mandate, compliance in preclinical behavioral neuroscience remains inconsistent. A 2021 review found that fewer than half of published preclinical studies adequately report sex-based analyses, and many still pool male and female data without testing for interaction effects [@warden2026].

The root cause is not a lack of statistical knowledge as most behavioral researchers are familiar with t-tests and regression. There is a lack of integrated infrastructure. Video-tracking platforms such as EthoVision XT and ANY-maze export data in vendor-specific CSV formats with inconsistent column names, encoding issues, and missing metadata. Converting these exports into an analysis-ready format, classifying subjects by sex (often inferred from cage-card numbers or subject IDs), checking for tracking artifacts, running the appropriate statistical tests, and producing figures that meet journal and NIH reporting standards typically involves a patchwork of manual Excel manipulation, lab-specific MATLAB or Python scripts, and copy-paste between programs.

There is no existing open-source tool that integrates these steps specifically for SABV compliance in preclinical behavioral neuroscience. General-purpose statistical platforms (e.g., R, SPSS, Prism) require the user to handle data ingestion, cleaning, and sex classification manually. Laboratory information management systems (LIMS) are designed for sample tracking, not behavioral analysis. The realistic alternative to NeuroPipe-SABV is therefore not a named competitor, but the inconsistent manual workflows that dominate the field.

NeuroPipe-SABV addresses this gap by providing a single, guided workflow that is accessible to researchers without programming expertise while remaining fully transparent and extensible for those who do code. The application has been used for behavioral data analysis in the Laboratory for Comparative Neuropsychology at Towson University, including open-field, elevated plus-maze, and Morris water-maze datasets.

# Functionality

NeuroPipe-SABV is organized as a seven-step guided analysis path:

1. Upload Data. Users upload CSV or Excel exports from EthoVision XT, ANY-maze, or other platforms. The ingestion layer attempts UTF-8, Latin-1, and cp1252 decoding to handle cross-platform encoding issues.

2. Process & Classify. The pipeline applies a standardized cleaning routine (strip column names, parse dates, drop duplicates, impute missing numeric values with the median, trim whitespace). Sex classification supports three modes: (a) threshold split on a numeric subject ID (e.g., IDs 1–16 = Male, 17–32 = Female), (b) manual comma-separated ID lists with range support (e.g., "1-16, 20, 22-24"), and (c) female-only list with all others assigned male. The classifier uses a regex-based parser that handles mixed ID formats such as "rat17", "subject_5", and "animal-123".

3. Analyze Differences. The pipeline performs Welch's two-sample t-tests (which do not assume equal variances) and calculates Cohen's d effect sizes for all numeric variables, stratified by sex. Standard error of the mean (SEM) is reported alongside means.

4. Create Visualizations. Distribution plots, boxplots, correlation heatmaps, and scatter plots are generated with matplotlib and seaborn. All figures are styled with a consistent dark theme and can be downloaded as PNG.

5. Build Models. Users can fit linear and polynomial regression models with train/test splitting, feature selection, and residual diagnostics using scikit-learn.

6. Download Results. The full processed dataset, summary statistics, and model outputs can be exported as formatted CSV or Excel workbooks.

7. Data Quality Controls. Throughout the workflow, the pipeline flags tracking artifacts (velocity spikes, frozen coordinates, coordinate jumps, out-of-bounds positions), missing values, and overlapping sex-classification ID lists.

# Design Decisions

Several engineering decisions distinguish NeuroPipe-SABV from a thin wrapper around pandas and scipy:

Header standardization. EthoVision XT and ANY-maze use different column vocabularies for the same measures (e.g., "X center" vs. "Centre point X", "Distance travelled" vs. "Path length").

The pipeline implements a three-tier matching strategy: exact, fuzzy (difflib, 0.85 cutoff), and substring, to map raw column names onto a canonical vocabulary. Collisions (multiple raw columns mapping to the same canonical name) are resolved with suffixed disambiguation. The mapping is extensible at runtime for lab-specific formats.

Sex-classification heuristics. Because many preclinical studies do not record sex explicitly in the tracking export, the pipeline infers it from subject identifiers. The parser handles prefixed labels ("rat17"), delimited labels ("subject_5"), and plain numerics, with vectorized application via pandas `.apply()` for efficiency.

Artifact detection. Rather than relying solely on missing-value counts, the pipeline implements five distinct detectors with rodent-appropriate thresholds: velocity spikes (>2 m/s), tracking dropouts (frozen coordinates for 5+ consecutive frames), coordinate jumps (>0.5 m between frames), missing-value patterns in required columns, and out-of-bounds positions. Detectors are grouped by animal ID to handle multi-subject datasets.

Welch's t-test and Cohen's d. The pipeline defaults to Welch's t-test because it does not assume equal variances which is a common issue in biological data where male and female groups often differ in variance as well as mean. Cohen's d is reported alongside p-values to distinguish statistical significance from practical significance, aligning with current SABV reporting recommendations.

# Acknowledgements

This work was supported by the Laboratory for Comparative Neuropsychology at Towson University. The authors thank the NIH for public guidance on SABV implementation. The authors have no competing interests to declare.
