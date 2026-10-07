# Contributing to NeuroPipe-SABV

I want this beta to improve through use, review, and criticism. Contributions can be code, statistical review, a reproducible failure, or an explanation of where the interface makes a decision difficult to inspect.

## Report a problem

Use the repository's issue templates. Include the task, expected and observed behavior, commit if known, Python/package versions, and a minimal synthetic or shareable example. For methodological feedback, describe the study design, experimental unit, and the assumption you are questioning. Do not upload confidential data.

## Development setup

Follow the root README's virtual-environment and dependency instructions. Tests use pytest:

```bash
python -m pip install pytest
python -m pytest test_pipeline.py test_header_mapping.py test_artifact_detection.py -v
```

Inspect `stress_tests.py` before running it. Record the exact command, environment, and results when reporting a test run. Passing checks do not establish validity for every study design.

## Pull requests

1. Create a focused branch from the current default branch.
2. Explain the research or workflow problem and the behavior your change introduces.
3. For calculation changes, include a small independently checkable example and relevant tests.
4. Update documentation when assumptions, inputs, or outputs change.
5. State limitations and any checks you could not complete.

Follow the style of the surrounding code. Avoid changing statistical behavior merely to make a figure look better or a result more significant.

For broader review questions, see [BETA_REVIEW.md](BETA_REVIEW.md). Use issues for discussion; no separate Discussions feature is required.
