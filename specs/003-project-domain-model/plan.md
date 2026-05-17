# Implementation Plan: Structured Project Domain Model

**Branch**: `003-project-domain-model` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-project-domain-model/spec.md`

## Summary

Python module `factor_lib.domain` that maps the raw `list[CsvRecord]` output
from `factor_lib.export` (feature 002) into a fully-typed, immutable domain object
graph. The module routes each record to the correct parser by `_source_file`, converts
Brazilian money strings to `Decimal`, parses date strings to `datetime.date`, and
normalizes `\xa0` null placeholders. Exposes a single Facade entry point
`build_projeto(records)` that returns a frozen `ProjetoCompleto` aggregate root.
Built TDD-first; 8 entity types derived from real `data/Projeto_372/` export data.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: stdlib only — `decimal`, `datetime`, `dataclasses`;
  reuses `CsvRecord` from `factor_lib.export` (feature 002)
**Storage**: N/A — pure data transformation; no I/O in this module
**Testing**: `pytest` (unit + integration); fixtures from `data/Projeto_372/`
**Target Platform**: Python library module — CI compatible
**Project Type**: library module (`factor_lib.domain`) inside existing `factor_lib` package
**Performance Goals**: Parse 239 records (Projeto 372) in < 1s; no external calls
**Constraints**: `Decimal` for money (no `float`); `datetime.date` for dates; zero new deps
**Scale/Scope**: Single-project export; 8 CSV types; hundreds of rows; single-process

## Constitution Check (v1.1.0)

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| §I TDD (NON-NEGOTIABLE) | ✅ PASS | All tasks: test written → FAIL → implement → PASS |
| §I Test pyramid | ✅ PASS | `tests/unit/domain/` (per parser) + `tests/integration/domain/` (full Projeto 372 fixture) |
| §II Python 3.11+ | ✅ PASS | Zero new deps; `decimal`, `datetime`, `dataclasses` are stdlib |
| §III OO + Patterns | ✅ PASS | Value Object (all entities frozen dataclasses), Strategy (registry), Facade (`build_projeto`) |
| §III SOLID | ✅ PASS | SRP: one parser per file; OCP: registry extensible without modifying builder |
| §IV Zero Anti-Patterns | ✅ PASS | No God Object (router+registry); DRY (`_clean`, `_parse_money` shared utils) |
| §V Playwright E2E | N/A | No browser in this module — pure domain transformation |

**Gate result**: All applicable principles satisfied. Proceeding to Phase 0.

**§V Note**: No E2E tests needed for this module — it is a pure library with no browser
interaction. Integration tests with real fixture data serve the same validation role.

## Project Structure

### Documentation (this feature)

```text
specs/003-project-domain-model/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── public-api.md    # Phase 1 output
└── tasks.md             # /speckit-tasks output
```

### Source Code — new files for this feature

```text
src/
  factor_lib/
    domain/
      __init__.py              # public re-exports: build_projeto, all parse_*, all data classes
      models.py                # 8 frozen dataclasses + ProjetoCompleto aggregate root
      exceptions.py            # DomainParseError(FactoLibError)
      builder.py               # build_projeto() — Facade + _PARSER_REGISTRY router
      parsers/
        __init__.py
        _utils.py              # _clean(), _parse_money(), _parse_date(), _parse_ref()
        projeto_info.py        # parse_project_info()
        equipe.py              # parse_equipe()
        pagamentos.py          # parse_pagamentos() — merges both payment CSV types
        plano_trabalho.py      # parse_plano_trabalho()
        recursos.py            # parse_recursos()
        documentos.py          # parse_documentos()
        prestacao_contas.py    # parse_prestacoes_contas()

tests/
  unit/domain/
    __init__.py
    test_models.py             # frozen dataclass contracts
    test_utils.py              # _clean(), _parse_money(), _parse_date()
    test_projeto_info.py       # parse_project_info() unit tests
    test_equipe.py             # parse_equipe() unit tests
    test_pagamentos.py         # parse_pagamentos() unit tests
    test_plano_trabalho.py     # parse_plano_trabalho() unit tests
    test_recursos.py           # parse_recursos() unit tests
    test_builder.py            # build_projeto() unit tests (mocked parsers)
  integration/domain/
    __init__.py
    conftest.py                # real_records fixture (loads data/Projeto_372/)
    test_build_projeto.py      # full integration test: real data → ProjetoCompleto

data/
  Projeto_372/                 # existing real fixture data (8 CSV files)
```

**Structure Decision**: Module added to existing `src/factor_lib/` tree as `domain/`.
Reuses `CsvRecord` from `factor_lib.export` (DRY, constitution §IV).
`parsers/` sub-package enforces Single Responsibility (one parser per file).

## Complexity Tracking

> No constitution violations. Table left intentionally empty.

**§V justification**: `factor_lib.domain` has no browser interaction — it receives
`list[CsvRecord]` (already downloaded and parsed by feature 002). E2E tests at this
level would only test the same Playwright flow already covered by feature 002 E2E tests.
The integration test with `data/Projeto_372/` real fixture data provides equivalent
coverage for this module.
