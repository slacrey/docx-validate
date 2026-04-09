# Local Dev Workflow Design

**Context:** The repository is a Python `src/` layout project. Running tests already works through pytest configuration, but local service startup depends on either editable install or an explicit `PYTHONPATH=src`, which is easy to miss.

**Decision:** Add a repository-level `Makefile` plus a small `scripts/dev.sh` launcher. The default workflow will depend on a local `.venv` virtual environment in the project root.

**Why this approach:**
- `make venv` and `make install` give an obvious first-run path.
- `make run` hides the `src` layout detail and enforces using `.venv`.
- A dedicated shell script keeps the startup logic readable and easier to extend than embedding everything in `Makefile`.

**Scope:**
- Add `Makefile` targets for environment creation, dependency installation, tests, local run, and cleanup.
- Add `scripts/dev.sh` to start uvicorn from the project root using `.venv/bin/python`.
- Update `.gitignore` for `.venv/`.
- Update README with the shortest working commands.

**Non-goals:**
- No Docker or process manager setup.
- No lint/format tooling changes.
- No production deployment scripts.
