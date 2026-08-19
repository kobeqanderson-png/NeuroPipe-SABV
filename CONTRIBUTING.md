# Contributing to NeuroPipe-SABV

Thank you for your interest in improving this project. This document covers how to report issues, propose changes, and run the test suite.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub and include:
- A minimal description of the problem
- Steps to reproduce (if applicable)
- Your Python version and operating system
- The output of `pip list` (or `requirements.txt` contents)

## Development Setup

```bash
git clone https://github.com/kobeqanderson-png/nihdatapipeline.git
cd nihdatapipeline
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest
```

## Running Tests

All tests are written with **pytest** and should be run with:

```bash
pytest test_pipeline.py -v
```

To run with coverage:

```bash
pytest test_pipeline.py --cov=src --cov-report=term-missing
```

## Pull Request Process

1. Fork the repository and create a feature branch (`git checkout -b feature/my-change`).
2. Ensure all tests pass locally before submitting (`pytest test_pipeline.py`).
3. Update documentation if your change affects user-facing behavior.
4. Open a pull request with a clear description of the change and its motivation.

## Code Style

- Follow PEP 8 for Python code.
- Add docstrings to new public functions.
- Keep functions focused and modular (see `src/cleaning.py` and `src/features.py` for examples).

## Questions?

Feel free to open a GitHub Discussion or email the maintainers.
