# `.vscode/` — why this is committed

Editor config is usually personal/global, but what's here is project-specific
and worth sharing:

- **`settings.json`** — tells VS Code's Testing panel this project uses
  pytest, with tests in `tests/`. Without it, VS Code can't discover/run/debug
  this repo's tests. Workspace settings layer *on top of* your own global
  User settings, so this doesn't affect other projects.
- **`launch.json`** — debug configs. "Python Debugger: Current File" runs
  whatever file is open as a plain script — for pytest test files, use the
  Testing sidebar (flask icon) or the inline "Debug Test" gutter icon
  instead, since a test file has no `if __name__ == "__main__":` to trigger
  when run directly.

**First-time setup:** make sure VS Code's selected Python interpreter (bottom
status bar) points at this project's `.venv` (created by `uv sync`), not a
global/other-project Python.
