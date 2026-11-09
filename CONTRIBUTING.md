# Contributing to NAVIQRA

Thanks for contributing. Open an issue for significant changes, include tests for behavior changes, document API/schema changes, and describe what was actually tested. Never commit secrets, provider credentials, or traveler data.

Run checks locally:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest -q
python -m compileall -q naviqra tests
```

Contributions are licensed under Apache-2.0.
