# Template Upload Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a synchronous template upload API that stores `.docx` template files, extracts reusable metadata, and supports explicit overwrite for the same template identity.

**Architecture:** Extend the existing FastAPI, SQLAlchemy, and local-storage stack with a dedicated template repository/service pair and a `.docx` metadata extractor. Keep the upload flow synchronous so the request performs hash calculation, duplicate checks, storage writes, metadata extraction, and record persistence in one pass.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, pytest, python-docx, zipfile/XML parsing where needed

---

### Task 1: Expand the template persistence model

**Files:**
- Modify: `src/docx_validate/models/template.py`
- Modify: `src/docx_validate/models/__init__.py`
- Create: `tests/db/test_template_model.py`

**Step 1: Write the failing test**

Add `tests/db/test_template_model.py` that inserts a `DocumentTemplate` and asserts:
- `name` and `version` are persisted
- `content_hash` is persisted
- `metadata_json` can be stored and loaded as a dictionary
- `status` defaults to `ACTIVE`
- duplicate `name + version` violates a uniqueness constraint

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/db/test_template_model.py -q`
Expected: FAIL because the model does not yet expose the new fields and constraints.

**Step 3: Write minimal implementation**

Update `DocumentTemplate` to add:
- `file_name`
- `file_size`
- `content_hash`
- `metadata_json`
- `updated_at`

Add database uniqueness constraints for:
- `name + version`
- `content_hash`

Ensure `metadata_json` uses a SQLAlchemy JSON-capable column and `status` defaults to `ACTIVE`.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/db/test_template_model.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/docx_validate/models/template.py src/docx_validate/models/__init__.py tests/db/test_template_model.py
git commit -m "feat: expand template persistence model"
```

### Task 2: Add template schemas and repository queries

**Files:**
- Create: `src/docx_validate/schemas/template.py`
- Modify: `src/docx_validate/schemas/__init__.py`
- Create: `src/docx_validate/repositories/template_repository.py`
- Modify: `src/docx_validate/repositories/__init__.py`
- Create: `tests/repositories/test_template_repository.py`

**Step 1: Write the failing tests**

Add `tests/repositories/test_template_repository.py` covering:
- create and fetch by `id`
- fetch by `name + version`
- fetch by `content_hash`
- update-and-save existing template records

Add schema assertions for:
- read payload exposes `id`, `name`, `version`, `status`, `object_key`, `file_name`, `file_size`, `content_hash`, and `metadata_json`

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/repositories/test_template_repository.py -q`
Expected: FAIL because the repository and schemas do not exist.

**Step 3: Write minimal implementation**

Create:
- `TemplateRead`
- any helper schema needed for service return values

Implement repository methods:
- `create(template)`
- `get(template_id)`
- `get_by_identity(name, version)`
- `get_by_content_hash(content_hash)`
- `save(template)`

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/repositories/test_template_repository.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/docx_validate/schemas/template.py src/docx_validate/schemas/__init__.py src/docx_validate/repositories/template_repository.py src/docx_validate/repositories/__init__.py tests/repositories/test_template_repository.py
git commit -m "feat: add template repository and schemas"
```

### Task 3: Build the metadata extractor for `.docx` templates

**Files:**
- Create: `src/docx_validate/services/template_metadata.py`
- Create: `tests/services/test_template_metadata.py`
- Create: `tests/fixtures/templates/basic-template.docx`
- Create: `tests/fixtures/templates/no-placeholders.docx`

**Step 1: Write the failing tests**

Add `tests/services/test_template_metadata.py` that loads fixture `.docx` files and asserts the extractor returns:
- `paragraph_count`
- `table_count`
- `section_count`
- `styles`
- `bookmarks`
- `placeholders`

Assert placeholder extraction recognizes simple text patterns like `{{ customer_name }}` and `${order_no}`.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/services/test_template_metadata.py -q`
Expected: FAIL because the extractor does not exist.

**Step 3: Write minimal implementation**

Create a metadata extraction service that:
- opens the `.docx` with `python-docx` for document structure
- reads underlying XML when needed for bookmarks
- normalizes metadata into a dictionary with stable keys
- returns an empty placeholder list when none are found

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/services/test_template_metadata.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/docx_validate/services/template_metadata.py tests/services/test_template_metadata.py tests/fixtures/templates/basic-template.docx tests/fixtures/templates/no-placeholders.docx
git commit -m "feat: add template metadata extraction"
```

### Task 4: Implement the template service with conflict and overwrite rules

**Files:**
- Create: `src/docx_validate/services/template_service.py`
- Modify: `src/docx_validate/services/__init__.py`
- Modify: `src/docx_validate/services/storage.py`
- Create: `tests/services/test_template_service.py`

**Step 1: Write the failing tests**

Add `tests/services/test_template_service.py` covering:
- creating a new template stores the file and metadata
- duplicate `name + version` is rejected when `overwrite=False`
- duplicate content hash under another identity is rejected
- `overwrite=True` updates the same database row
- same identity plus same content behaves idempotently when `overwrite=True`

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/services/test_template_service.py -q`
Expected: FAIL because the service does not exist.

**Step 3: Write minimal implementation**

Implement a template service that:
- validates `.docx` uploads
- computes `sha256`
- builds a deterministic `object_key`
- writes bytes through `LocalStorage`
- calls the metadata extractor
- creates or updates the template row according to the approved overwrite rules

Add small storage helpers only if the service needs them. Do not redesign the storage abstraction for remote object stores in this iteration.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/services/test_template_service.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/docx_validate/services/template_service.py src/docx_validate/services/__init__.py src/docx_validate/services/storage.py tests/services/test_template_service.py
git commit -m "feat: add template upload service"
```

### Task 5: Add template API routes

**Files:**
- Create: `src/docx_validate/api/routes/templates.py`
- Modify: `src/docx_validate/api/routes/__init__.py`
- Modify: `src/docx_validate/api/__init__.py`
- Create: `tests/api/test_templates.py`

**Step 1: Write the failing tests**

Add `tests/api/test_templates.py` covering:
- `POST /api/v1/templates` success response
- reject non-`.docx` uploads with HTTP `400`
- reject duplicate `name + version` with HTTP `409`
- reject duplicate content hash under another identity with HTTP `409`
- allow overwrite with `overwrite=true`
- `GET /api/v1/templates/{id}` success and `404` responses

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/api/test_templates.py -q`
Expected: FAIL because the route does not exist.

**Step 3: Write minimal implementation**

Create the template routes, wire them into the API router, and translate service exceptions into the standard response envelope with stable error codes.

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/api/test_templates.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/docx_validate/api/routes/templates.py src/docx_validate/api/routes/__init__.py src/docx_validate/api/__init__.py tests/api/test_templates.py
git commit -m "feat: add template upload api"
```

### Task 6: Document the template API and developer fixtures

**Files:**
- Modify: `README.md`

**Step 1: Update the README**

Document:
- the two template endpoints
- multipart fields for upload
- duplicate and overwrite semantics
- the metadata extraction scope for this iteration

**Step 2: Run focused regression tests plus the full suite**

Run:
- `python3 -m pytest tests/db/test_template_model.py tests/repositories/test_template_repository.py tests/services/test_template_metadata.py tests/services/test_template_service.py tests/api/test_templates.py -q`
- `python3 -m pytest -q`

Expected:
- focused tests PASS
- full suite PASS

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document template upload api"
```
