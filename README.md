# NeuroPipe-SABV

A Streamlit web application that automates the analysis of preclinical 
behavioral neuroscience data in compliance with the NIH Sex as a Biological 
Variable (SABV) policy.

**[Try the live app →](https://data-analysis-sabv.streamlit.app/)**

![Research Hub Screenshot](screenshot.png)

---

## The Problem

Preclinical behavioral labs running EthoVision or ANY-maze generate messy, 
inconsistent CSV exports. Cleaning, classifying sex, checking for artifacts, 
running statistics, and producing publication-ready figures is tedious, 
error-prone, and time-consuming — often taking hours per dataset. On top of 
that, NIH now requires SABV compliance, meaning sex must be treated as a 
biological variable in all federally funded research. Most labs handle this 
manually and inconsistently.

## The Solution

This pipeline takes raw EthoVision or ANY-maze exports and automates the 
entire workflow:

- **Standardizes headers** across inconsistent export formats
- **Classifies sex** automatically from subject IDs or metadata
- **Detects artifacts** and flags data quality issues
- **Runs statistical tests** including group comparisons and regressions
- **Verifies group balance** between sexes and conditions
- **Generates publication-ready visualizations** with SABV-compliant reporting

Upload your CSV. Get clean, analyzed, visualized results — in minutes, not hours.

## NIH SABV Compliance

The pipeline is built around the NIH mandate that sex be included as a 
biolog
