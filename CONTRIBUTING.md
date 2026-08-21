# Contributing

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows, use `.venv\Scripts\activate.bat` instead of `source`.

## Checks

Run these before opening a pull request:

```bash
ruff check .
pytest
```

## Pull Request Expectations

- Keep generated files, virtual environments, model weights, and videos out of Git.
- Add or update tests for analytics, config, or tracking lifecycle changes.
- Document new CLI/config options in `README.md` and `config/default.yaml`.
- Include a short before/after note for changes that affect counting behavior.
