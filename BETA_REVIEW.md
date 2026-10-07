# NeuroPipe-SABV beta review

**Current status: public research beta.** This is a set of questions for review, not a certification or completed validation report.

| Review area | Question | Useful check |
| --- | --- | --- |
| Import | Do headers, units, and rows retain their meaning? | Compare a small source file with the imported table |
| Sex metadata | Does classification match the study's explicit metadata? | Include IDs that violate the default numeric convention |
| Cleaning | What changes when missing values or duplicates are handled? | Trace original rows through processing |
| Experimental unit | Are trials or sessions mistakenly treated as independent subjects? | Inspect subject/session structure before a group comparison |
| Inference | Are tests and effect sizes appropriate for the design? | Compare a specified example with a separate reference calculation |
| Multiplicity | What happens when many variables or models are explored? | State the tested family and intended correction/interpretation |
| Interactions | Does the question require a sex-by-treatment interaction? | Check the model rather than inferring an interaction from separate p-values |
| Visualization | Do labels, sample sizes, and uncertainty describe the analysis correctly? | Match each figure to its input and calculation |

## Existing evidence

The repository contains `test_pipeline.py`, `stress_tests.py`, `test_header_mapping.py`, and `test_artifact_detection.py`, plus a historical `TEST_RESULTS.md`. The historical report contains stated results from April 2026. They have not been independently reproduced as part of this documentation revision. A test count is not the same as measured code coverage, and a synthetic-data check is not validation across real study designs.

## Report a review

Include the commit, environment, exact command/workflow, a minimal shareable input, expected and observed results, and a reference calculation if relevant. State what the check supports and what it leaves unresolved.
