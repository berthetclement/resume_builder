# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF).

## Stack

- Project and dependency management: **uv** (no manual pip/venv — use `uv add`, `uv sync`, `uv run`).
- Build backend: **hatchling**.
- Python version: floor `>=3.11` (`requires-python`), dev on **3.13**.

## Available commands

```bash
uv sync      # installs deps and creates/syncs the .venv
uv build     # generates wheel + sdist in dist/
uv run python -c "import resume_builder"   # sanity-checks that the package imports
```

## Current state

Skeleton only (`uv init --package`). No business logic, no tests, no dependencies added yet. Structure and conventions to be defined as implementation progresses.