# Document Validation Bootstrap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first runnable backend slice for the `.docx` validation service: FastAPI app, persistent task records, and task creation/status APIs.

**Architecture:** Start with a small FastAPI service backed by SQLAlchemy and local file storage abstractions so the upload and task lifecycle can be exercised end-to-end in tests. Keep the detection engine and async worker behind placeholders for later batches, but shape the code so Celery, MinIO, and rule/template modules can be added without rewrites.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, pytest, httpx, anyio

---

### Task 1: Bootstrap the application and test harness

**Files:**
- Create: `pyproject.toml`
- Create: `src/docx_validate/__init__.py`
- Create: `src/docx_validate/main.py`
- Create: `src/docx_validate/config.py`
- Create: `src/docx_validate/api/__init__.py`
- Create: `src/docx_validate/api/routes/__init__.py`
- Create: `src/docx_validate/api/routes/health.py`
- Create: `tests/conftest.py`
- Create: `tests/api/test_health.py`

**Step 1: Write the failing test**

Add `tests/api/test_health.py` with an async API test that requests `GET /api/v1/health` and asserts:
- HTTP 200
- `{"code": 0, "message": "ok", "data": {"status": "ok"}}`

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/api/test_health.py -q`
Expected: FAIL because the package/app does not exist yet.

**Step 3: Write minimal implementation**

Create the Python project metadata, app factory, settings, and health route. Mount the route at `/api/v1/health` and return the standard envelope.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/api/test_health.py -q`
Expected: PASS.

### Task 2: Add database session management and task persistence model

**Files:**
- Create: `src/docx_validate/db/__init__.py`
- Create: `src/docx_validate/db/base.py`
- Create: `src/docx_validate/db/session.py`
- Create: `src/docx_validate/models/__init__.py`
- Create: `src/docx_validate/models/task.py`
- Create: `tests/db/test_task_model.py`
- Modify: `tests/conftest.py`

**Step 1: Write the failing test**

Add `tests/db/test_task_model.py` to create a database session, insert a `DocumentTask`, flush/commit, and assert:
- `task_no` is persisted and unique
- initial `status` is `PENDING`
- `progress` defaults to `0`

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/db/test_task_model.py -q`
Expected: FAIL because the ORM/session layer does not exist.

**Step 3: Write minimal implementation**

Create SQLAlchemy declarative base, engine/session helpers, and a `DocumentTask` model with the fields needed for the first API slice (`task_no`, `template_id`, `rule_set_id`, `input_object_key`, `status`, `progress`, `error_message`, `created_at`, `finished_at`).

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/db/test_task_model.py -q`
Expected: PASS.

### Task 3: Implement task creation and task status query APIs

**Files:**
- Create: `src/docx_validate/api/deps.py`
- Create: `src/docx_validate/api/routes/tasks.py`
- Create: `src/docx_validate/repositories/__init__.py`
- Create: `src/docx_validate/repositories/task_repository.py`
- Create: `src/docx_validate/schemas/__init__.py`
- Create: `src/docx_validate/schemas/task.py`
- Create: `src/docx_validate/services/__init__.py`
- Create: `src/docx_validate/services/storage.py`
- Create: `src/docx_validate/services/task_service.py`
- Create: `tests/api/test_tasks.py`
- Modify: `src/docx_validate/main.py`
- Modify: `tests/conftest.py`

**Step 1: Write the failing tests**

Add `tests/api/test_tasks.py` covering:
- `POST /api/v1/tasks` accepts a `.docx` upload plus `template_id` and `rule_set_id`
- response envelope includes a generated `task_no`, `status=PENDING`, and `progress=0`
- uploaded file is stored under `inputs/{task_no}/source.docx`
- `GET /api/v1/tasks/{task_no}` returns the persisted task
- uploading a non-`.docx` file returns HTTP 400 and `code=40001`

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/api/test_tasks.py -q`
Expected: FAIL because the task routes and services do not exist.

**Step 3: Write minimal implementation**

Add task schemas, repository/service logic, filesystem-backed upload storage for the test/dev environment, and API routes for create/query. Reuse the standard response envelope and keep task execution asynchronous work out of scope for now.

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/api/test_tasks.py -q`
Expected: PASS.

### Task 4: Add template and rule-set metadata stubs

**Files:**
- Create: `src/docx_validate/models/template.py`
- Create: `src/docx_validate/models/rule_set.py`
- Create: `src/docx_validate/api/routes/rules.py`
- Create: `tests/api/test_rules.py`

**Step 1: Write failing tests for creating and fetching rule sets.**

**Step 2: Run the rule API tests and confirm failure.**

**Step 3: Implement the minimal rule-set metadata model and API.**

**Step 4: Re-run the rule API tests and confirm success.**

### Task 5: Add placeholder validation execution flow

**Files:**
- Create: `src/docx_validate/services/validator.py`
- Modify: `src/docx_validate/services/task_service.py`
- Create: `tests/services/test_task_service.py`

**Step 1: Write a failing service test for transitioning a task from `PENDING` to `SUCCESS` with a stub summary.**

**Step 2: Run the service test and confirm failure.**

**Step 3: Implement a synchronous placeholder validator that records an empty report artifact.**

**Step 4: Re-run the service test and confirm success.**

### Task 6: Add developer documentation and local run instructions

**Files:**
- Create: `README.md`

**Step 1: Write the README with setup, test, and dev-run commands matching the implemented project layout.**

**Step 2: Verify the documented commands against the current codebase.**
