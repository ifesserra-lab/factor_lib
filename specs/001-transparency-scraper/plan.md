# Implementation Plan: Transparency Portal Scraper Library

**Branch**: `001-transparency-scraper` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-transparency-scraper/spec.md`

## Summary

Python library (`factor_lib`) that automates scraping of project data from the
Facto transparency portal (`https://facto.conveniar.com.br/portaltransparencia/`).
Uses Playwright for browser automation with a Page Object Model architecture.
Exposes a simple public API: list projects, scrape details, save to JSON.
Built TDD-first with pytest + pytest-playwright; OO design with Strategy, Facade,
and Factory patterns; zero anti-patterns per constitution.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `playwright` (sync API), `pytest`, `pytest-playwright`,
  `mypy`, `ruff`, `dataclasses-json`
**Storage**: JSON files (local filesystem)
**Testing**: `pytest` (unit/integration) + `pytest-playwright` (E2E); POM pattern
**Target Platform**: Linux / macOS, headless — suitable for CI environments
**Project Type**: library
**Performance Goals**: Sequential scraping; no throughput SLA for v1
**Constraints**: Public portal (no auth); sequential project iteration; headless mode
**Scale/Scope**: Single portal; hundreds of projects; single-process execution

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Test-First (TDD) | ✅ PASS | All tasks ordered: test written → fails → implement |
| II. Python | ✅ PASS | Python 3.11+; `pyproject.toml`; PEP 8; type hints everywhere |
| III. OO + Design Patterns | ✅ PASS | POM, Strategy, Facade, Factory; SOLID throughout |
| IV. Zero Anti-Patterns | ✅ PASS | DI for browser/page; no singletons; no God objects |
| V. Playwright E2E | ✅ PASS | `pytest-playwright`; POM enforced; network mocking in tests |

**Gate result**: All principles satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-transparency-scraper/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── public-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
factor_lib/                         # repo root
├── pyproject.toml
├── src/
│   └── factor_lib/
│       ├── __init__.py             # public re-exports
│       ├── api.py                  # Facade: high-level public API
│       ├── browser.py              # BrowserFactory + context lifecycle
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── base_page.py        # BasePage POM class
│       │   └── portal_page.py      # TransparencyPortalPage (listing + detail)
│       ├── scrapers/
│       │   ├── __init__.py
│       │   ├── base_scraper.py     # AbstractScraper (Strategy interface)
│       │   ├── listing_scraper.py  # ListingScraper (Strategy impl)
│       │   └── detail_scraper.py   # DetailScraper (Strategy impl)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── project.py          # ProjectListingRecord, ProjectDetailRecord
│       │   └── result.py           # ScrapeResult
│       └── serializers/
│           ├── __init__.py
│           └── json_serializer.py  # save_to_json
└── tests/
    ├── conftest.py                 # shared pytest fixtures
    ├── unit/
    │   ├── test_models.py
    │   ├── test_serializers.py
    │   └── test_scrapers.py
    ├── integration/
    │   └── test_api.py
    └── e2e/
        ├── conftest.py             # playwright fixtures; recorded snapshots
        └── test_portal.py          # Playwright E2E tests
```

**Structure Decision**: Single-project library layout. Source under `src/factor_lib/`
(src-layout prevents import of uninstalled package). Tests separated by scope:
unit (no I/O), integration (filesystem), E2E (Playwright browser).

## Complexity Tracking

> No constitution violations in this design. Table left intentionally empty.
