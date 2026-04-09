# Template Upload Design

**Context:** The service already supports rule-set metadata, document task creation, local file storage, and a placeholder validation flow. Template support currently exists only as a bare SQLAlchemy model, so callers cannot register template files, query template metadata, or enforce template identity rules before creating validation tasks.

**Goal:** Add a template upload slice that stores `.docx` template files, extracts reusable structural metadata synchronously, and enforces both business-identity and file-content deduplication rules.

## Decision

Implement a synchronous template API with two endpoints:

- `POST /api/v1/templates`
- `GET /api/v1/templates/{template_id}`

`POST /templates` accepts multipart form data with `name`, `version`, optional `overwrite`, and the `.docx` file. The request completes file hashing, duplicate detection, local storage write, structural metadata extraction, and template record persistence before returning.

## Why This Approach

- It matches the current project shape, where uploads and task creation are processed synchronously inside the request lifecycle.
- It avoids coupling template registration to the future async execution system, which is a separate iteration item.
- It gives downstream task creation a stable `template_id` and a ready-to-use `metadata_json` payload without needing extra background orchestration.
- It keeps failure handling explicit: the API can return conflicts or extraction errors immediately.

## Domain Model

Expand `DocumentTemplate` to include the minimum fields needed for upload, overwrite, and metadata extraction:

- `id`
- `name`
- `version`
- `status`
- `object_key`
- `file_name`
- `file_size`
- `content_hash`
- `metadata_json`
- `created_at`
- `updated_at`

### Constraints

- `UNIQUE(name, version)` defines the business identity of a template version.
- `UNIQUE(content_hash)` ensures the same file content cannot be registered under multiple identities.

### Status Values

Keep status as a first-class field even though this iteration is synchronous:

- `ACTIVE`
- `PROCESSING`
- `FAILED`
- `INACTIVE`

This preserves forward compatibility for a later async extraction flow without forcing a model rewrite now.

## API Contract

### `POST /api/v1/templates`

**Request**

`multipart/form-data` with:

- `name`: string
- `version`: string
- `overwrite`: optional boolean-like field, default `false`
- `file`: `.docx` upload

**Success**

- HTTP `201`
- Standard envelope: `{ "code": 0, "message": "ok", "data": ... }`

**Failure**

- HTTP `400` for invalid file extension or malformed request fields
- HTTP `409` for identity conflicts or content-hash conflicts
- HTTP `422` when the file is a `.docx` but metadata extraction cannot parse the document structure
- HTTP `500` for unexpected system failures

### `GET /api/v1/templates/{template_id}`

Returns the persisted template metadata using the existing standard response envelope. Missing records return HTTP `404`.

## Conflict Semantics

The API must distinguish between identity and content conflicts:

- Same `name + version`, `overwrite=false`: reject with HTTP `409`
- Same `name + version`, `overwrite=true`: allow overwrite of that exact template record
- Same `content_hash` but different template identity: reject with HTTP `409`
- Same `name + version` and same `content_hash`:
  - reject when `overwrite=false`
  - treat as an idempotent overwrite when `overwrite=true`

`overwrite=true` only authorizes replacing the stored file and metadata for the existing `name + version` record. It does not allow rebinding a file already owned by another template identity.

## Upload Flow

Handle `POST /templates` in this order:

1. Validate multipart fields and ensure the upload ends with `.docx`.
2. Read the file bytes and compute:
   - `content_hash` using `sha256`
   - `file_size`
3. Query by `content_hash` and by `name + version` to determine the exact conflict branch.
4. Persist the file through the existing local storage abstraction.
5. Extract structural metadata from the `.docx`.
6. Create or update the template record.
7. Return the stored template payload.

For storage layout, place files under a deterministic object key such as:

- `templates/{name}/{version}/{content_hash}.docx`

If the project later needs identity-safe path normalization, the storage key builder can be tightened without changing the API contract.

## Metadata Extraction Scope

Only extract metadata that is both stable and immediately useful for later validation rules. The first pass should include:

- `document`
  - `paragraph_count`
  - `table_count`
  - `section_count`
  - `core_properties`
- `styles`
  - distinct style names used or available in the document
- `bookmarks`
  - bookmark names discovered from the Word XML structure
- `placeholders`
  - text placeholders matching simple patterns such as `{{ name }}` and `${name}`
- `extracted_at`

Do not promise support in this iteration for:

- content controls
- complex merge fields
- comments, tracked changes, or revision markup
- complete WordprocessingML introspection

The metadata payload should be stored as a stable JSON object in `metadata_json`, not as free-form text.

## Overwrite Behavior

Overwrite updates the same template row instead of creating a replacement row. On overwrite:

- preserve `id`
- replace `object_key`
- replace `file_name`
- replace `file_size`
- replace `content_hash`
- replace `metadata_json`
- update `updated_at`
- keep `status=ACTIVE` on success

If extraction fails after the new file has been written, mark the template `FAILED` only when updating an existing row inside the same flow is safe and deterministic. Otherwise, fail the request and avoid partial database writes.

## Testing Strategy

Cover the slice at three levels:

- API tests for success, `.docx` validation, duplicate identity rejection, content-hash conflict rejection, overwrite success, and `GET /templates/{id}`
- repository/service tests for conflict resolution and overwrite-updates-same-row behavior
- extractor tests for paragraph/table/style/bookmark/placeholder extraction and empty-placeholder documents

Use committed fixture `.docx` files or programmatically generated test documents so the extraction layer is exercised against real Word content instead of mocked dictionaries.

## Non-goals

This iteration deliberately excludes:

- template list or pagination APIs
- template delete/deactivate APIs
- batch uploads
- async extraction or worker integration
- CSV/JSON issue reports
- annotated output `.docx`

## Follow-on Work

This design intentionally sets up later iterations:

- async template processing can reuse `status` and `metadata_json`
- validation rules can consume extracted `placeholders`, `styles`, and `bookmarks`
- report-generation work can reference a richer template record without changing task creation contracts
