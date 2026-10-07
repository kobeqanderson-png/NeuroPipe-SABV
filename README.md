# NeuroPipe-SABV

**Public research beta · Open source under MIT · Methodological review invited**

I built NeuroPipe-SABV to explore a question from behavioral research: how can sex as a biological variable stay visible as we move from raw data to analysis and interpretation?

The project brings data preparation, sex-based grouping, visualization, and statistical exploration into a Streamlit workflow. I want researchers to be able to try it, inspect its assumptions, and challenge the parts that need work. A polished figure is not evidence that the analysis behind it is appropriate.

[Open the beta app](https://data-analysis-sabv.streamlit.app/) · [Review priorities and limitations](BETA_REVIEW.md) · [Report a problem](https://github.com/kobeqanderson-png/NeuroPipe-SABV/issues/new/choose)

![Existing NeuroPipe-SABV interface screenshot](screenshot.png)

## What exists

The repository includes workflows for CSV/Excel ingestion, data inspection and cleaning, sex classification using configured metadata/ID conventions, group comparisons, feature transformations, visualization, regression, and result export. Export formats and study designs vary: support must be checked on a representative example of your own data.

## What “SABV” means here

SABV means **sex as a biological variable**. NIH's policy addresses research design, analysis, and reporting in vertebrate animal and human studies. This software does not certify NIH compliance, establish an appropriate design, or replace methodological judgment. It is an independent project, not an NIH endorsement.

Read the [NIH policy](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-15-102.html) alongside the assumptions of your actual study. Producing sex-stratified figures alone does not settle the design or analysis questions.

## Try it locally

```bash
git clone https://github.com/kobeqanderson-png/NeuroPipe-SABV.git
cd NeuroPipe-SABV
python -m venv .venv
# Activate: source .venv/bin/activate (macOS/Linux)
# Or: .venv\Scripts\Activate.ps1 (Windows PowerShell)
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use a synthetic or non-sensitive example first. Before interpreting outputs:

1. Check the imported columns, units, missing values, and subject identifiers against the source.
2. Verify sex assignments against explicit study metadata. Numeric ID thresholds encode a study-specific convention; they do not determine sex independently.
3. Inspect cleaning, duplicate removal, missing-value handling, and transformations. Record any changes to the data.
4. Identify the experimental unit and repeated observations. Do not interpret rows as independent animals when they are trials, sessions, or repeated measurements.
5. Evaluate the statistical model, multiplicity, and interpretation for your research question. A sex comparison is not automatically a test of a sex-by-treatment interaction.
6. Compare a small result with a separately calculated reference before relying on it.

## Evidence and limitations

Tests and historical test reports are included in the repository. They are useful starting material, not proof of general scientific validity or production readiness. The [beta review page](BETA_REVIEW.md) separates current review priorities from historical reports. This documentation revision does not claim to rerun or independently verify every historical test result.

Important review areas include schema compatibility, metadata inference, repeated measurements, missing-data assumptions, multiple comparisons, and interpretation of exploratory models. Broad independent validation across labs and study designs is not established here.

Some older technical documents describe earlier versions and use stronger readiness or compliance language. Treat those documents as historical; the beta scope above is the current project positioning.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). Code review, statistical criticism, unexpected results, and confusing workflows all help. A small, reproducible example is more useful than a general statement that something did not work.

Please share only data you have permission to disclose. Synthetic examples are usually sufficient for bug reports.

## Citation and license

Cite the software repository and the release or commit you actually used. Author metadata is in [`codemeta.json`](codemeta.json); confirm publication details separately before citing a journal article.

[MIT License](LICENSE) · [Kobe Anderson's portfolio](https://kobeport.vercel.app/)
