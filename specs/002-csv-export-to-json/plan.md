# Implementation Plan: CSV Export to JSON Processor

**Branch**: `002-csv-export-to-json` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-csv-export-to-json/spec.md`

## Summary

Python module `factor_lib.export` that automates CSV data export from the Facto
transparency portal's project detail page. Uses Playwright to click "Exportar em CSV",
downloads the resulting ZIP to a library-managed temp dir, parses all CSVs inside
(with encoding fallback), and saves structured records to JSON. Packaged inside the
existing `factor_lib` package — reuses `save_to_json` and `BrowserFactory` from core.
Built TDD-first with pytest + pytest-playwright; OO with Strategy, Facade, Value Object.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `playwright` (sync API), `pytest`, `pytest-playwright`,
  `mypy`, `ruff` — all stdlib for ZIP/CSV: `zipfile`, `csv`, `tempfile`, `io`
**Storage**: JSON files (local filesystem); temp dir auto-deleted after parse
**Testing**: `pytest` (unit/integration) + `pytest-playwright` (E2E); POM pattern
**Target Platform**: Linux / macOS headless — CI compatible
**Project Type**: library module (`factor_lib.export`) inside existing package
**Performance Goals**: 60-second download timeout (configurable); sequential processing
**Constraints**: No auth; temp dir lifecycle managed by library; no live portal in CI
**Scale/Scope**: Per-project export; single ZIP; hundreds of CSV rows; single-process

## Constitution Check (v1.1.0)

*GATE: Must pass before Phase 0. Re-check after Phase 1.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| §I TDD (NON-NEGOTIABLE) | ✅ PASS | All tasks.md test tasks precede impl tasks; Red commit → Green commit enforced |
| §I Test pyramid | ✅ PASS | `tests/unit/export/`, `tests/integration/export/`, `tests/e2e/export/` — all three levels |
| §II Python 3.11+ | ✅ PASS | stdlib only for ZIP/CSV; no new deps beyond playwright already required |
| §III OO + Patterns | ✅ PASS | Strategy (csv_parser), Facade (exporter), Factory (browser shared), Value Object (CsvRecord) |
| §IV Zero Anti-Patterns | ✅ PASS | DI for page/browser; `save_to_json` reused (DRY); no singletons |
| §V Playwright E2E | ✅ PASS | `pytest-playwright`; POM via `TransparencyPortalPage`; `page.route()` mocking |

**Gate result**: All principles satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-csv-export-to-json/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── public-api.md    # Phase 1 output
└── tasks.md             # Already generated (/speckit-tasks)
```

### Source Code — new files for this feature

```text
src/
  factor_lib/
    export/
      __init__.py          # public re-exports for factor_lib.export
      downloader.py        # download_csv_export() — Playwright download + temp dir
      csv_parser.py        # parse_zip_csv() — ZIP extraction + CSV parsing (Strategy)
      exporter.py          # export_project_csv_to_json() — Facade
      models.py            # CsvRecord, ExportResult frozen dataclasses (Value Object)
      exceptions.py        # ExportError hierarchy

tests/
  unit/export/
    test_models.py
    test_downloader.py
    test_csv_parser.py
    test_exporter.py
  integration/export/
    test_save.py
    test_export_flow.py
  e2e/export/
    conftest.py            # Playwright fixtures + route mocking helpers
    test_csv_export.py     # Full E2E with page.route() ZIP mock
    fixtures/
      sample_export.zip    # Recorded ZIP fixture (real portal structure)
```

**Structure Decision**: Module added to existing `src/factor_lib/` tree.
Shared utilities (`save_to_json`, `BrowserFactory`) reused from feature 001 — no duplication.

## Complexity Tracking

> No constitution violations. Table left intentionally empty.
