# Repository Guidelines

## Project Structure & Module Organization
- Root files include `main.py` (CLI entry point) and `pyproject.toml` (metadata, Python >=3.13).
- Virtual environments should live in `.venv/` or `venv/`; keep them git-ignored.
- When the logic grows, create a package directory `makeandroidicon/` for modules, keeping `main.py` as a thin launcher.
- Place tests under `tests/` mirroring module names; commit fixtures or sample assets under `tests/fixtures/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create and activate a local virtual environment if one is not already present.
- `pip install -e .` — install the project in editable mode so module imports resolve during development.
- `python main.py` — run the current CLI stub and verify entrypoint wiring.
- `pip install -r requirements-dev.txt` — optional; add and install dev tooling requirements when the file is created.

## Coding Style & Naming Conventions
- Target Python 3.13+ and follow PEP 8: four-space indentation, snake_case for functions and variables, CapWords for classes.
- Keep `main.py` focused on argument parsing and orchestration; push business logic into package modules.
- Before committing, format with `black` and lint with `ruff` (add them to `requirements-dev.txt` if not already present).

## Testing Guidelines
- Use `pytest` for all new tests; name files `test_<feature>.py`.
- Run `pytest` from the repo root to pick up the default discovery rules.
- Include edge-case scenarios for icon sizes and invalid inputs as fixtures.
- Aim for high coverage on image transformation utilities; document gaps in the PR if coverage drops.

## Commit & Pull Request Guidelines
- With no existing history, adopt Conventional Commits (e.g., `feat: add adaptive icon generator`) for clarity.
- Keep commits focused and documented; explain context and intent in the body when behavior changes.
- PRs should link to tracking issues, describe testing performed, and attach before/after artifacts (e.g., generated icons) when relevant.
- Request review once CI (when added) is green and outstanding TODOs are resolved.

## Agent Workflow Tips
- Always run commands from `/Users/shioken/develop/makeAndroidIcon`.
- Respect the workspace-write sandbox by limiting edits to tracked project files.
- Document any new tooling or folder you introduce directly in this guide to keep it authoritative.
- Communicate with the user in Japanese.
