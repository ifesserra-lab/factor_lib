# Tasks: Transparency Portal Scraper Library

**Input**: Design documents from `specs/001-transparency-scraper/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/public-api.md ✅

**TDD**: MANDATORY (constitution §I) — every implementation task MUST have a failing test written first (RED), then implementation (GREEN).

**Existing**: `serializers/json_serializer.py` (generic save_to_json), `exceptions.py` (FactoLibError), directory structure (pages/, scrapers/, models/, tests/e2e/unit/integration/) — all empty __init__.py files created.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure test infrastructure

- [x] T001 Install playwright and chromium browser: `.venv/bin/playwright install chromium` (run from repo root)
- [x] T002 [P] Create `tests/conftest.py` with shared browser context fixture for unit/integration tests (no live browser, stub-based)
- [x] T003 [P] Create `tests/e2e/conftest.py` with pytest-playwright fixtures, `page.route()` network mock helper, and snapshot loader utility
- [x] T004 [P] Record portal listing HTML snapshot to `tests/e2e/fixtures/portal_listing.html` (navigate to portal, click Consultar, save rendered HTML)
- [x] T005 [P] Record portal detail HTML snapshot to `tests/e2e/fixtures/portal_detail.html` (click first lupa, save rendered detail HTML/modal)

**Checkpoint**: Playwright installed, E2E fixture snapshots captured, test infrastructure ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, exceptions, and browser factory shared by all user stories. Tests written first (RED), then implemented (GREEN).

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

### RED: Tests for foundational components

- [x] T006 [P] Write failing unit tests for `PortalNavigationError` in `tests/unit/test_exceptions.py` (assert it is a subclass of FactoLibError, carries message)
- [x] T007 [P] Write failing unit tests for `ProjectListingRecord` in `tests/unit/test_models.py` (frozen dataclass, required fields id/name/raw_row, immutability)
- [x] T008 [P] Write failing unit tests for `ProjectDetailRecord` in `tests/unit/test_models.py` (frozen dataclass, required fields, _error defaults to None, serialization shape)
- [x] T009 [P] Write failing unit tests for `ScrapeResult` in `tests/unit/test_models.py` (frozen dataclass, total == success_count + error_count invariant, records tuple length == total)
- [x] T010 [P] Write failing unit tests for `BrowserFactory` in `tests/unit/test_browser.py` (creates context with correct headless flag and timeout, context manager protocol)
- [x] T011 [P] Write failing unit tests for `BasePage` in `tests/unit/test_pages.py` (constructor stores page reference, wait helper delegates to page.wait_for_selector)

### GREEN: Implement foundational components

- [x] T012 Add `PortalNavigationError` to `src/factor_lib/exceptions.py` (subclass of FactoLibError)
- [x] T013 [P] Implement `ProjectListingRecord` frozen dataclass in `src/factor_lib/models/project.py`
- [x] T014 [P] Implement `ProjectDetailRecord` frozen dataclass in `src/factor_lib/models/project.py` (fields: id, name, fields, _source_url, _scraped_at, _error=None)
- [x] T015 [P] Implement `ScrapeResult` frozen dataclass in `src/factor_lib/models/result.py` (records: tuple, total, success_count, error_count, started_at, completed_at)
- [x] T016 [P] Update `src/factor_lib/models/__init__.py` to re-export ProjectListingRecord, ProjectDetailRecord, ScrapeResult
- [x] T017 Implement `BrowserFactory` in `src/factor_lib/browser.py` (creates Playwright sync browser context; headless param; timeout param; context manager)
- [x] T018 Implement `BasePage` in `src/factor_lib/pages/base_page.py` (stores page reference; `wait_for(selector, timeout)` helper; `wait_for_network_idle()` helper)
- [x] T019 Update `src/factor_lib/pages/__init__.py` to re-export BasePage
- [x] T020 Update `src/factor_lib/__init__.py` to export PortalNavigationError, ProjectListingRecord, ProjectDetailRecord, ScrapeResult

**Checkpoint**: All foundational tests GREEN — user story phases can now proceed

---

## Phase 3: User Story 1 — List All Projects (Priority: P1) 🎯 MVP

**Goal**: `list_projects()` navigates to portal, clicks Consultar, returns list of ProjectListingRecord

**Independent Test**: Call `list_projects()` with mocked portal HTML → assert returns non-empty list of ProjectListingRecord with id and name populated

### RED: Tests for US1

- [x] T021 [P] [US1] Write failing unit tests for `AbstractScraper` protocol in `tests/unit/test_scrapers.py` (has `scrape(page)` method signature)
- [x] T022 [P] [US1] Write failing unit tests for `ListingScraper` in `tests/unit/test_scrapers.py` (scrape() returns list[ProjectListingRecord]; handles empty table; extracts id from link href or row data; extracts name from row text)
- [x] T023 [P] [US1] Write failing E2E test for `list_projects()` in `tests/e2e/test_portal.py` using `portal_listing.html` snapshot via `page.route()` (assert result is list, len > 0, each item is ProjectListingRecord)

### GREEN: Implement US1

- [x] T024 [US1] Implement `AbstractScraper` ABC in `src/factor_lib/scrapers/base_scraper.py` (abstract `scrape(page: Page) -> Any` method)
- [x] T025 [US1] Implement `TransparencyPortalPage.click_consultar()` and `TransparencyPortalPage.get_listing_rows()` in `src/factor_lib/pages/portal_page.py` (extends BasePage; locator for Consultar button `#ctl00_ContentPlaceHolder1_ProjetosUserControl1_lnkConsultarProjetos`; extract all rows via `a:has-text("Visualizar os detalhes")`)
- [x] T026 [US1] Implement `ListingScraper` in `src/factor_lib/scrapers/listing_scraper.py` (implements AbstractScraper; calls portal_page.click_consultar(); calls portal_page.get_listing_rows(); maps rows to ProjectListingRecord with sequential id fallback)
- [x] T027 [US1] Implement `list_projects()` in `src/factor_lib/api.py` (uses BrowserFactory + TransparencyPortalPage + ListingScraper; headless param; timeout param; returns list[ProjectListingRecord])
- [x] T028 [US1] Update `src/factor_lib/scrapers/__init__.py` to re-export AbstractScraper and ListingScraper
- [x] T029 [US1] Update `src/factor_lib/__init__.py` to export `list_projects`

**Checkpoint**: `list_projects()` returns all portal projects using mocked HTML fixture → US1 independently testable

---

## Phase 4: User Story 2 — Scrape Project Details (Priority: P2)

**Goal**: `scrape_all_projects()` iterates each listing record, clicks lupa, scrapes all labelled fields, returns ScrapeResult with all ProjectDetailRecord instances

**Independent Test**: Call `scrape_all_projects()` with mocked listing + detail HTML → assert ScrapeResult.total == N records, each has non-empty fields dict, failed records have _error set

### RED: Tests for US2

- [x] T030 [P] [US2] Write failing unit tests for `DetailScraper` in `tests/unit/test_scrapers.py` (scrape() returns list[ProjectDetailRecord]; clicks lupa for each listing record; extracts all labelled field pairs; on per-project failure sets _error and continues; adds _scraped_at and _source_url)
- [x] T031 [P] [US2] Write failing E2E test for `scrape_all_projects()` in `tests/e2e/test_portal.py` using both listing and detail HTML snapshots via `page.route()` (assert ScrapeResult.total > 0, success_count + error_count == total, records have fields)
- [x] T032 [P] [US2] Write failing unit tests for error-tolerance in `tests/unit/test_scrapers.py` (when lupa click raises, DetailScraper catches, sets _error, continues to next project)

### GREEN: Implement US2

- [x] T033 [US2] Implement `TransparencyPortalPage.click_detail_icon(record)` and `TransparencyPortalPage.get_detail_fields()` in `src/factor_lib/pages/portal_page.py` (click lupa link adjacent to project row; wait for detail view/modal; extract all label→value pairs as dict)
- [x] T034 [US2] Implement `DetailScraper` in `src/factor_lib/scrapers/detail_scraper.py` (implements AbstractScraper; iterates ProjectListingRecord list; for each: clicks lupa, waits for detail, extracts fields via portal_page.get_detail_fields(); on exception: logs error, sets _error; always continues; adds _scraped_at ISO timestamp, _source_url)
- [x] T035 [US2] Implement `scrape_all_projects()` in `src/factor_lib/api.py` (uses BrowserFactory + TransparencyPortalPage + ListingScraper + DetailScraper; captures started_at/completed_at; builds ScrapeResult; raises PortalNavigationError only if listing fails)
- [x] T036 [US2] Update `src/factor_lib/scrapers/__init__.py` to re-export DetailScraper
- [x] T037 [US2] Update `src/factor_lib/__init__.py` to export `scrape_all_projects`

**Checkpoint**: `scrape_all_projects()` with mocked fixtures returns all detail records, one-project-failure does not abort run → US2 independently testable

---

## Phase 5: User Story 3 — Save Results to JSON (Priority: P3)

**Goal**: `save_to_json()` accepts list[ProjectDetailRecord] or ScrapeResult and writes valid JSON to path; `scrape_and_save()` orchestrates full flow end-to-end

**Independent Test**: Pass known list of ProjectDetailRecord to `save_to_json(records, tmp_path)` → file exists, is valid JSON array, len matches, each record has merged fields

### RED: Tests for US3

- [x] T038 [P] [US3] Write failing unit tests for updated `save_to_json` in `tests/unit/test_serializers.py` (accepts list[ProjectDetailRecord]; fields merged to root dict; _source_url, _scraped_at, _error at root; accepts ScrapeResult and extracts .records)
- [x] T039 [P] [US3] Write failing integration tests in `tests/integration/test_api.py` (call save_to_json with known records and tmp_path; assert file exists, valid JSON, len correct, overwrite behavior, parent dir auto-creation)
- [x] T040 [P] [US3] Write failing integration test for `scrape_and_save()` in `tests/integration/test_api.py` (mock scrape_all_projects via patch; assert file written, ScrapeResult returned)

### GREEN: Implement US3

- [x] T041 [US3] Update `src/factor_lib/serializers/json_serializer.py` to: (1) handle ScrapeResult by extracting .records; (2) serialize ProjectDetailRecord by merging fields dict into root with _source_url, _scraped_at, _error as top-level keys
- [x] T042 [US3] Implement `scrape_and_save()` in `src/factor_lib/api.py` (calls scrape_all_projects(), then save_to_json(); returns ScrapeResult; propagates PortalNavigationError and OSError)
- [x] T043 [US3] Update `src/factor_lib/__init__.py` to export `save_to_json`, `scrape_and_save`, and all data model classes

**Checkpoint**: All three user stories independently functional and tested → ready for polish phase

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Integration validation, public API completeness, and final review

- [x] T044 [P] Write integration test for full `scrape_and_save()` flow in `tests/integration/test_api.py` with all browser calls mocked via `unittest.mock.patch` (no live portal needed)
- [x] T045 [P] Add `__all__` to `src/factor_lib/__init__.py` with complete public API surface (list_projects, scrape_all_projects, save_to_json, scrape_and_save, ProjectListingRecord, ProjectDetailRecord, ScrapeResult, PortalNavigationError)
- [x] T046 Run quickstart.md scenario validation: execute `scrape_and_save("output/projects.json")` against live portal and verify output JSON is non-empty valid array
- [x] T047 [P] Verify all ruff lint rules pass: `ruff check src/ tests/` with zero errors
- [x] T048 [P] Verify mypy type checking passes: `mypy src/factor_lib` with zero errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; T004/T005 require live portal access
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on Phase 2 — no dependency on US2 or US3
- **US2 (Phase 4)**: Depends on Phase 2 — depends on US1 for TransparencyPortalPage listing methods (T025)
- **US3 (Phase 5)**: Depends on Phase 2 — depends on US2 for ScrapeResult (T035)
- **Polish (Phase 6)**: Depends on all previous phases

### Within Each Phase

- RED tasks (failing tests) MUST be written and confirmed failing before GREEN implementation tasks
- Models before scrapers; scrapers before API; API before integration tests
- [P]-marked tasks within same phase can run concurrently

### Parallel Opportunities

- T006–T011 (foundational RED tests) can all run in parallel
- T013–T016 (model implementations) can run in parallel
- T021–T023 (US1 RED tests) can run in parallel
- T030–T032 (US2 RED tests) can run in parallel
- T038–T040 (US3 RED tests) can run in parallel
- T047–T048 (lint + type check) can run in parallel

---

## Parallel Example: Phase 2 RED tests

```bash
# All these can run concurrently (different files):
Task T006: "Write failing unit tests for PortalNavigationError in tests/unit/test_exceptions.py"
Task T007: "Write failing unit tests for ProjectListingRecord in tests/unit/test_models.py"
Task T008: "Write failing unit tests for ProjectDetailRecord in tests/unit/test_models.py"
Task T009: "Write failing unit tests for ScrapeResult in tests/unit/test_models.py"
Task T010: "Write failing unit tests for BrowserFactory in tests/unit/test_browser.py"
Task T011: "Write failing unit tests for BasePage in tests/unit/test_pages.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (RED → GREEN)
3. Complete Phase 3: US1 (RED → GREEN)
4. **STOP and VALIDATE**: `list_projects()` returns all portal projects via mocked fixture
5. Can already deliver: a library that lists all transparency projects

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → `list_projects()` works (MVP!)
3. US2 → `scrape_all_projects()` works (adds full detail data)
4. US3 → `scrape_and_save()` works (adds persistence)
5. Each phase adds value without breaking previous

### Key Locators (discovered from portal exploration)

- Consultar button: `#ctl00_ContentPlaceHolder1_ProjetosUserControl1_lnkConsultarProjetos`
- Project detail links: `a:has-text("Visualizar os detalhes")`
- Export CSV button: `a:has-text("Exportar para CSV")` (for future feature 002 integration)

---

## Notes

- [P] tasks = different files, no dependencies — safe to run concurrently
- TDD order is non-negotiable: RED commit → GREEN commit per constitution §I
- Portal uses dynamic JS rendering; always `wait_for_load_state("networkidle")` after navigation
- E2E tests MUST use recorded HTML snapshots via `page.route()` — never hit live portal in CI
- Playwright sync API throughout (no async) — see research.md Decision 1
- `_source_url` for scraper records should be the portal URL (same URL used for all — modal pattern)
