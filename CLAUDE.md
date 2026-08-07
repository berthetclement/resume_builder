# resume-builder

Python lib to generate resumes (Markdown -> HTML/PDF).

## Stack

- Project and dependency management: **uv** (no manual pip/venv — use `uv add`, `uv sync`, `uv run`).
- Build backend: **hatchling**.
- Python version: floor `>=3.11` (`requires-python`), dev on **3.13**.
- Dev tooling: **ruff** (lint + format), **mypy** (strict), **pytest**, **pre-commit**, **tox** (+ `tox-uv`).
- Dev dependencies are split into PEP 735 groups in `pyproject.toml`: `lint`, `type`, `test`, and `dev` (which includes all three plus `pre-commit`/`tox`/`tox-uv`). Plain `uv sync` installs everything via the `dev` group.
- CI: GitHub Actions (`.github/workflows/ci.yml`), matrix over Windows/Linux/macOS, runs `tox -p` (envs: `py311`, `py312`, `py313`, `lint`, `type`) on every push to any branch.

## Available commands

```bash
uv sync                                    # installs deps (project + dev group) and creates/syncs the .venv
uv build                                   # generates wheel + sdist in dist/
uv run python -c "import resume_builder"   # sanity-checks that the package imports

uv run pre-commit install                  # one-time per clone: wires up the git commit hook
uv run pre-commit run --all-files          # run ruff check/format + mypy against the whole repo

uv run ruff check .                        # lint
uv run mypy src                            # type-check (strict)
uv run pytest                              # run tests
uv run tox -p                              # run the full matrix (py311/py312/py313/lint/type) locally, same as CI
```

## Current state

DevOps scaffolding in place (pre-commit, ruff, mypy strict, pytest, tox, CI) per the "no feature before a complete lib setup" principle. No business logic yet — only the `resume_builder.main()` skeleton. Tests live in `tests/` at the repo root.