# Local Dev Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a predictable local development workflow with `.venv`-based install, test, and run commands.

**Architecture:** Keep the entrypoints thin. `Makefile` exposes stable developer commands, while `scripts/dev.sh` owns runtime setup for uvicorn and hides the Python `src` layout detail by exporting `PYTHONPATH=src`.

**Tech Stack:** GNU Make, POSIX shell, Python 3.11, pytest, uvicorn

---

### Task 1: Add regression tests for developer entrypoints

**Files:**
- Create: `tests/test_dev_workflow.py`

**Step 1: Write the failing tests**

Add tests that assert:
- `scripts/dev.sh` exits non-zero with a clear message when `.venv/bin/python` does not exist.
- `Makefile` defines `venv`, `install`, `test`, `run`, and `clean` targets and delegates `run` to `scripts/dev.sh`.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_dev_workflow.py -q`
Expected: FAIL because the script and Makefile do not exist yet.

**Step 3: Write minimal implementation**

Create `Makefile`, `scripts/dev.sh`, and supporting ignore/doc updates needed to satisfy the workflow.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_dev_workflow.py -q`
Expected: PASS.

### Task 2: Update developer documentation

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`

**Step 1: Document the first-run and day-to-day commands.**

**Step 2: Run the focused tests plus the full test suite.**
