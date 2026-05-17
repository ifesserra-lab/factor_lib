---
description: "Task list for CSV Export to JSON Processor"
---

# Tasks: CSV Export to JSON Processor

**Input**: Design documents from `specs/002-csv-export-to-json/`
**Branch**: `002-csv-export-to-json`
**Prerequisites**: spec.md ✅ | clarifications ✅ | constitution §I TDD mandatory

**TDD MANDATORY (constitution §I)**: Every test task MUST be written and confirmed
FAILING before the corresponding implementation task begins. No exceptions.

**Module**: `src/factor_lib/export/` — packaged inside `factor_lib` (same package as
feature 001). Shared utilities (`save_to_json`, `BrowserFactory`) reused from core.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[Story]**: User story (US1–US4) — omitted in Setup/Foundational/Polish phases
- All paths relative to repo root

---

## Phase 1: Setup

**Purpose**: Create module skeleton and test infrastructure

- [x] T001 Create directory structure: `src/factor_lib/export/`, `tests/unit/export/`, `tests/integration/export/`, `tests/e2e/export/fixtures/`
- [x] T002 [P] Create empty `__init__.py` files in each new package directory
- [x] T003 [P] Add `tests/e2e/export/fixtures/sample_export.zip` — record a real ZIP fixture from the portal (or create minimal valid ZIP with one CSV for mocking)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data models and exceptions shared across all user stories

**⚠️ CRITICAL**: No user story work begins until this phase is complete

- [x] T004 Write failing test for CsvRecord dataclass fields and frozen immutability in `tests/unit/export/test_models.py`
- [x] T005 [P] Write failing test for ExportResult dataclass fields and invariants in `tests/unit/export/test_models.py`
- [x] T006 [P] Write failing test for ExportError hierarchy (inherits from FactoLibError) in `tests/unit/export/test_models.py`
- [x] T007 Implement `CsvRecord` and `ExportResult` dataclasses in `src/factor_lib/export/models.py`
- [x] T008 [P] Implement `ExportError` exception class in `src/factor_lib/export/exceptions.py`
- [x] T009 Wire public re-exports in `src/factor_lib/export/__init__.py`: `ExportError`, `CsvRecord`, `ExportResult`, `download_csv_export`, `parse_zip_csv`, `export_project_csv_to_json`

**Checkpoint**: Models and exceptions green — user story work may begin

---

## Phase 3: User Story 1 — Trigger CSV Export Download (P1) 🎯 MVP

**Goal**: Library clicks "Exportar em CSV", waits for download (max 60s), stores ZIP
in library-managed temp dir, deletes temp dir automatically after use.

**Independent Test**: `download_csv_export(page)` on mocked detail page → assert
bytes returned and no temp files left on disk after call.

### Tests for User Story 1 ⚠️ Write FIRST — must FAIL before T014

- [x] T010 [P] [US1] Write failing unit test: `download_csv_export` raises `ExportError` when "Exportar em CSV" button not found in `tests/unit/export/test_downloader.py`
- [x] T011 [P] [US1] Write failing unit test: `download_csv_export` raises `ExportError` on timeout (mock download taking >60s) in `tests/unit/export/test_downloader.py`
- [x] T012 [P] [US1] Write failing unit test: `download_csv_export` follows redirect and downloads from final URL in `tests/unit/export/test_downloader.py`
- [x] T013 [P] [US1] Write failing E2E test: `download_csv_export` with `page.route()` mock intercepting ZIP download, assert temp dir cleaned up after call in `tests/e2e/export/test_csv_export.py`

### Implementation for User Story 1

- [x] T014 [US1] Implement `download_csv_export(page, *, timeout: int = 60_000) -> bytes` in `src/factor_lib/export/downloader.py`:
  - Locate "Exportar em CSV" button; raise `ExportError` if not found
  - Use Playwright download event; follow redirects automatically
  - Download ZIP to `tempfile.TemporaryDirectory()` (context manager)
  - Raise `ExportError` if download not complete within `timeout` ms
  - Return ZIP bytes; temp dir deleted on exit (success or failure)

**Checkpoint**: US1 independently functional — `download_csv_export` passes all tests

---

## Phase 4: User Story 2 — Extract and Parse CSV from ZIP (P2)

**Goal**: Accept ZIP bytes, enumerate CSVs inside, parse rows as dicts, handle
encoding fallbacks, skip empty rows, tag multi-file records with source filename.

**Independent Test**: `parse_zip_csv(zip_bytes)` with `tests/e2e/export/fixtures/sample_export.zip`
→ assert non-empty list of dicts with expected column keys.

### Tests for User Story 2 ⚠️ Write FIRST — must FAIL before T022

- [x] T015 [P] [US2] Write failing unit test: `parse_zip_csv` with single-CSV ZIP returns list of dicts, keys = CSV headers in `tests/unit/export/test_csv_parser.py`
- [x] T016 [P] [US2] Write failing unit test: `parse_zip_csv` with multi-CSV ZIP merges rows, each record has `_source_file` in `tests/unit/export/test_csv_parser.py`
- [x] T017 [P] [US2] Write failing unit test: `parse_zip_csv` with ZIP containing no CSVs returns `[]` and logs warning in `tests/unit/export/test_csv_parser.py`
- [x] T018 [P] [US2] Write failing unit test: `parse_zip_csv` with Latin-1 CSV falls back from UTF-8 and parses correctly in `tests/unit/export/test_csv_parser.py`
- [x] T019 [P] [US2] Write failing unit test: empty rows skipped silently; mismatched-column rows get `""` for missing fields in `tests/unit/export/test_csv_parser.py`
- [x] T020 [P] [US2] Write failing unit test: each record includes `_extracted_at` (ISO 8601) and `_source_file` metadata in `tests/unit/export/test_csv_parser.py`

### Implementation for User Story 2

- [x] T021 [P] [US2] Implement `parse_zip_csv(zip_bytes: bytes) -> list[CsvRecord]` in `src/factor_lib/export/csv_parser.py`:
  - Open ZIP from bytes with `zipfile.ZipFile`
  - Enumerate members; filter to `.csv` extension only (ignore others silently)
  - For each CSV: try UTF-8 decode; fallback to Latin-1/ISO-8859-1 on `UnicodeDecodeError`
  - Parse with `csv.DictReader`; skip rows where all values are empty (debug-log count)
  - Rows shorter than headers: missing columns default to `""`
  - Tag each record: `_source_file=<filename>`, `_extracted_at=<ISO 8601 now>`
  - Return list of frozen `CsvRecord` instances

**Checkpoint**: US1 + US2 independently functional and testable

---

## Phase 5: User Story 3 — Save Parsed Records to JSON (P3)

**Goal**: Serialize list of `CsvRecord` to JSON file at caller-specified path,
creating intermediate directories. Reuse `save_to_json` from `factor_lib` core.

**Independent Test**: Call `save_to_json(records, path)` → file at `path` is valid
JSON array with same record count.

### Tests for User Story 3 ⚠️ Write FIRST — must FAIL before T025

- [x] T022 [P] [US3] Write failing integration test: `save_to_json` with `CsvRecord` list creates valid JSON file in `tests/integration/export/test_save.py`
- [x] T023 [P] [US3] Write failing integration test: `save_to_json` overwrites existing file in `tests/integration/export/test_save.py`
- [x] T024 [P] [US3] Write failing integration test: `save_to_json` creates missing parent directories in `tests/integration/export/test_save.py`

### Implementation for User Story 3

- [x] T025 [US3] Verify `save_to_json` from `src/factor_lib/serializers/json_serializer.py` (feature 001) handles `CsvRecord` dataclasses correctly via `default=str`. Add `CsvRecord` serialization test to existing serializer tests if needed. No new implementation — reuse core.

**Checkpoint**: US1 + US2 + US3 independently functional

---

## Phase 6: User Story 4 — End-to-End Export Flow (P4)

**Goal**: Single-call facade `export_project_csv_to_json(page, output_path)` composes
download → parse → save. Guarantees temp cleanup via `try/finally`. Surfaces errors
with stage label.

**Independent Test**: `export_project_csv_to_json(page, "output/test.json")` with
Playwright mock → `output/test.json` exists and contains expected records.

### Tests for User Story 4 ⚠️ Write FIRST — must FAIL before T029

- [x] T026 [P] [US4] Write failing integration test: `export_project_csv_to_json` produces valid JSON file with all records from fixture ZIP in `tests/integration/export/test_export_flow.py`
- [x] T027 [P] [US4] Write failing unit test: download failure raises `ExportError` with message "download stage failed: <reason>" in `tests/unit/export/test_exporter.py`
- [x] T028 [P] [US4] Write failing unit test: parse failure raises `ExportError` with message "parse stage failed: <reason>" in `tests/unit/export/test_exporter.py`
- [x] T029 [P] [US4] Write failing E2E test: full flow with `page.route()` mock produces JSON file in `tests/e2e/export/test_csv_export.py`

### Implementation for User Story 4

- [x] T030 [US4] Implement `export_project_csv_to_json(page, output_path, *, timeout: int = 60_000) -> ExportResult` in `src/factor_lib/export/exporter.py`:
  - Call `download_csv_export(page, timeout=timeout)` → ZIP bytes
  - Call `parse_zip_csv(zip_bytes)` → list of CsvRecord
  - Call `save_to_json(records, output_path)`
  - Wrap each stage in try/except; re-raise as `ExportError(f"<stage> stage failed: {e}")`
  - Return `ExportResult(records=..., total=..., ...)`
- [x] T031 [US4] Update `src/factor_lib/export/__init__.py` — confirm all public symbols exported correctly

**Checkpoint**: All 4 user stories independently functional and tested

---

## Phase N: Polish & Cross-Cutting Concerns

- [x] T032 [P] Run `mypy --strict src/factor_lib/export/` — fix all type errors
- [x] T033 [P] Run `ruff check src/factor_lib/export/ tests/unit/export/ tests/integration/export/ tests/e2e/export/` — fix all warnings
- [x] T034 [P] Verify no anti-patterns present: God Objects, magic strings, Singleton abuse, copy-paste (constitution §IV review)
- [x] T035 Run `pytest tests/unit/export tests/integration/export tests/e2e/export` — confirm all green
- [x] T036 Update `docs/backlog.md` — mark feature 002 US status as Concluído ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks all user stories
- **US1 (Phase 3)**: Depends on Foundational — no dependency on US2/US3/US4
- **US2 (Phase 4)**: Depends on Foundational — no dependency on US1
- **US3 (Phase 5)**: Depends on Foundational — reuses core serializer
- **US4 (Phase 6)**: Depends on US1 + US2 + US3 completion
- **Polish (Phase N)**: Depends on all user stories complete

### TDD Order Within Each User Story

```
Write test → Confirm FAIL → Implement → Confirm PASS → Refactor → Keep PASS
```

### Parallel Opportunities

```bash
# Phase 2 — all foundational tests can run in parallel:
T004, T005, T006  # test models and exceptions

# Phase 3 — all US1 tests can start in parallel:
T010, T011, T012, T013  # US1 tests

# Phase 4 — all US2 tests in parallel:
T015, T016, T017, T018, T019, T020  # US2 tests

# Phase 5 — all US3 tests in parallel:
T022, T023, T024  # US3 tests

# Phase 6 — all US4 tests in parallel:
T026, T027, T028, T029  # US4 tests

# Polish — all quality checks in parallel:
T032, T033, T034  # type check, lint, anti-pattern review
```

---

## Implementation Strategy

### MVP (User Story 1 only)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational — models + exceptions)
3. Complete Phase 3 (US1 — download + temp dir lifecycle)
4. **VALIDATE**: `pytest tests/unit/export/test_downloader.py tests/e2e/export/` — all green
5. Demo: `download_csv_export(page)` returns bytes; no temp files left

### Incremental Delivery

1. Setup + Foundational → skeleton ready
2. US1 → download works independently → validate
3. US2 → CSV parsing works independently → validate
4. US3 → save works (reuses core) → validate
5. US4 → full flow in one call → validate

---

## Notes

- `[P]` = different files, no shared write target, safe to run in parallel
- Tests marked with ⚠️ **must fail** before implementation — TDD is non-negotiable (constitution §I)
- `save_to_json` is reused from feature 001 (`src/factor_lib/serializers/json_serializer.py`) — no duplication (DRY, constitution §IV)
- Temp dir cleanup guaranteed by `try/finally` in `downloader.py` — no resource leaks in CI
- E2E tests use `page.route()` mocking — no live portal required (constitution §V)
- Commit pattern: test commit (RED) → implementation commit (GREEN) → refactor commit (optional)
