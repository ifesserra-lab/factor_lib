---
description: "Task list for feature 003: Structured Project Domain Model"
---

# Tasks: Structured Project Domain Model

**Feature**: `003-project-domain-model`
**Input**: Design documents from `specs/003-project-domain-model/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅

**Tests**: TDD is NON-NEGOTIABLE (constitution §I). Tests written FIRST → must FAIL → implement → must PASS.

**Organization**: Tasks grouped by user story. Phase 2 (Foundational) MUST complete before any user story work begins.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup (Module Skeleton)

**Purpose**: Create the `factor_lib.domain` package tree and all `__init__.py` files so imports work from the start.

- [x] T001 Create directory tree: `src/factor_lib/domain/`, `src/factor_lib/domain/parsers/`, `tests/unit/domain/`, `tests/integration/domain/`
- [x] T002 [P] Create empty `src/factor_lib/domain/__init__.py` (public re-exports added later)
- [x] T003 [P] Create empty `src/factor_lib/domain/parsers/__init__.py`
- [x] T004 [P] Create empty `tests/unit/domain/__init__.py`
- [x] T005 [P] Create empty `tests/integration/domain/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Exceptions, models, and utility helpers that every parser depends on. MUST complete before any user story work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests (TDD — write FIRST, confirm RED)

- [x] T006 [P] Write unit tests for `DomainParseError` in `tests/unit/domain/test_exceptions.py` — assert `stage`, `reason` attributes and `str()` representation
- [x] T007 [P] Write unit tests for all 8 frozen dataclasses in `tests/unit/domain/test_models.py` — assert frozen (`FrozenInstanceError` on mutation), correct field types, and `__eq__` by value
- [x] T008 [P] Write unit tests for `_clean()`, `_parse_money()`, `_parse_date()` in `tests/unit/domain/test_utils.py` — parametrize with `\xa0`, empty string, valid/invalid money, valid/invalid date strings

### Implementation (after T006–T008 are RED)

- [x] T009 Implement `DomainParseError(FactoLibError)` with `stage: str` and `reason: str` in `src/factor_lib/domain/exceptions.py`
- [x] T010 Implement all 8 frozen dataclasses (`ProjetoInfo`, `MembroEquipe`, `Pagamento`, `ItemPlanoTrabalho`, `RecursoRubrica`, `Documento`, `PrestacaoContas`, `ProjetoCompleto`) in `src/factor_lib/domain/models.py`
- [x] T011 Implement `_clean()`, `_parse_money()`, `_parse_date()`, `_parse_ref()` in `src/factor_lib/domain/parsers/_utils.py`

**Checkpoint**: Run `pytest tests/unit/domain/test_exceptions.py tests/unit/domain/test_models.py tests/unit/domain/test_utils.py` — all GREEN before proceeding.

---

## Phase 3: User Story 1 — Parse Project Info (Priority: P1) 🎯 MVP

**Goal**: `parse_project_info(records)` returns a typed `ProjetoInfo` with all 12 fields.

**Independent Test**: Call with fixture records from `Informações do projeto.csv` and assert `referencia == "372"`, `data_inicio` is `datetime.date`, `valor_aprovado` is `Decimal`.

### Tests for User Story 1 (TDD — write FIRST, confirm RED)

- [x] T012 [US1] Write unit tests for `parse_project_info()` in `tests/unit/domain/test_projeto_info.py`:
  - valid record → `ProjetoInfo` with correct types for all 12 fields
  - `referencia` normalized to `"372"` from `"372 - Estudos..."` string
  - empty record list → raises `DomainParseError`
  - optional field `data_encerramento` absent → `None`
  - optional fields `departamento`, `processo` as `\xa0` → `None`

### Implementation for User Story 1 (after T012 is RED)

- [x] T013 [US1] Implement `parse_project_info(records: list[CsvRecord]) -> ProjetoInfo` in `src/factor_lib/domain/parsers/projeto_info.py`

**Checkpoint**: `pytest tests/unit/domain/test_projeto_info.py` — all GREEN.

---

## Phase 4: User Story 2 — Parse Team Members (Priority: P2)

**Goal**: `parse_equipe(records)` returns `list[MembroEquipe]` with `vinculada_executora` as bool.

**Independent Test**: Call with 19 fixture records and assert count, `vinculada_executora` is bool, `\xa0` fields are `None`.

### Tests for User Story 2 (TDD — write FIRST, confirm RED)

- [x] T014 [US2] Write unit tests for `parse_equipe()` in `tests/unit/domain/test_equipe.py`:
  - valid records → list with correct count and field types
  - `"Sim"` in `Vinculada à inst. executora` → `vinculada_executora == True`
  - `"Não"` → `vinculada_executora == False`
  - `\xa0` in `carga_horaria`, `grau_instrucao`, `vinculo`, `instituicao` → `None`
  - empty record list → returns `[]`

### Implementation for User Story 2 (after T014 is RED)

- [x] T015 [US2] Implement `parse_equipe(records: list[CsvRecord]) -> list[MembroEquipe]` in `src/factor_lib/domain/parsers/equipe.py`

**Checkpoint**: `pytest tests/unit/domain/test_equipe.py` — all GREEN.

---

## Phase 5: User Story 3 — Parse Financial Data (Priority: P3)

**Goal**: `parse_pagamentos(records)` merges both payment CSV types into `list[Pagamento]` with `valor: Decimal`.

**Independent Test**: Call with 21 fixture records (5 pessoa física + 16 servidores) and assert total count = 21, all `valor` are `Decimal`, `tipo_favorecido` set correctly per source file.

### Tests for User Story 3 (TDD — write FIRST, confirm RED)

- [x] T016 [US3] Write unit tests for `parse_pagamentos()` in `tests/unit/domain/test_pagamentos.py`:
  - records from `pagamento de pessoa física.csv` → `tipo_favorecido == "pessoa_fisica"`
  - records from `pagamento de servidores ou agentes públicos.csv` → `tipo_favorecido == "servidor"`
  - `valor` field `"3.722.800,00"` → `Decimal("3722800.00")`
  - masked CPF `"***.506.767-**"` stored as-is
  - `data_pagamento` as `datetime.date`
  - both CSV types merged into single list
  - empty record list → returns `[]`

### Implementation for User Story 3 (after T016 is RED)

- [x] T017 [US3] Implement `parse_pagamentos(records: list[CsvRecord]) -> list[Pagamento]` in `src/factor_lib/domain/parsers/pagamentos.py`

**Checkpoint**: `pytest tests/unit/domain/test_pagamentos.py` — all GREEN.

---

## Phase 6: User Story 4 — Parse Work Plan and Resources (Priority: P4)

**Goal**: `parse_plano_trabalho()` returns 185 typed items; `parse_recursos()` returns 11 typed budget records.

**Independent Test**: Call `parse_plano_trabalho()` with 185 fixture records and assert all `valor_total_aprovado` are `Decimal`, all `\xa0` → `None`.

### Tests for User Story 4 (TDD — write FIRST, confirm RED)

- [x] T018 [P] [US4] Write unit tests for `parse_plano_trabalho()` in `tests/unit/domain/test_plano_trabalho.py`:
  - valid records → list of `ItemPlanoTrabalho` with correct types
  - `\xa0` in `codigo`, `produto`, `agrupamento`, `descricao`, `justificativa` → `None`
  - `valor_total_aprovado` and `valor_executado` as `Decimal`
  - blank `valor_unitario` → `None`
  - empty record list → returns `[]`
- [x] T019 [P] [US4] Write unit tests for `parse_recursos()` in `tests/unit/domain/test_recursos.py`:
  - valid records → list of `RecursoRubrica` with `aprovado`, `liberado`, `executado` as `Decimal`
  - `moeda` field stored as-is
  - empty record list → returns `[]`

### Implementation for User Story 4 (after T018 and T019 are RED)

- [x] T020 [P] [US4] Implement `parse_plano_trabalho(records: list[CsvRecord]) -> list[ItemPlanoTrabalho]` in `src/factor_lib/domain/parsers/plano_trabalho.py`
- [x] T021 [P] [US4] Implement `parse_recursos(records: list[CsvRecord]) -> list[RecursoRubrica]` in `src/factor_lib/domain/parsers/recursos.py`
- [x] T022 [P] [US4] Implement `parse_documentos(records: list[CsvRecord]) -> list[Documento]` in `src/factor_lib/domain/parsers/documentos.py`
- [x] T023 [P] [US4] Implement `parse_prestacoes_contas(records: list[CsvRecord]) -> list[PrestacaoContas]` in `src/factor_lib/domain/parsers/prestacao_contas.py`

**Checkpoint**: `pytest tests/unit/domain/test_plano_trabalho.py tests/unit/domain/test_recursos.py` — all GREEN.

---

## Phase 7: User Story 5 — Assemble ProjetoCompleto (Priority: P5)

**Goal**: `build_projeto(records)` routes all records by `_source_file`, calls each parser, assembles and returns frozen `ProjetoCompleto`.

**Independent Test**: Call with all 239 records from `data/Projeto_372/` and assert `info.referencia == "372"`, `len(equipe) == 19`, `len(pagamentos) == 21`, `len(plano_trabalho) == 185`, `len(recursos) == 11`.

### Tests for User Story 5 (TDD — write FIRST, confirm RED)

- [x] T024 [US5] Write unit tests for `build_projeto()` with mocked parsers in `tests/unit/domain/test_builder.py`:
  - records for each `_source_file` → correct parser called
  - unknown `_source_file` → silently ignored (no error)
  - missing CSV type → empty tuple in `ProjetoCompleto`
  - missing `ProjetoInfo` records → raises `DomainParseError`
  - returns frozen `ProjetoCompleto`
- [x] T025 [US5] Write integration test with real `data/Projeto_372/` fixture in `tests/integration/domain/test_build_projeto.py`:
  - conftest.py fixture loads all 8 CSVs via `parse_zip_csv` or direct CSV read
  - assert `info.referencia == "372"`
  - assert `len(equipe) == 19`
  - assert `len(pagamentos) == 21`
  - assert `len(plano_trabalho) == 185`
  - assert `len(recursos) == 11`
  - assert `sum(p.valor for p in projeto.pagamentos)` matches expected total
  - assert no field in any sub-entity contains `"\xa0"`

### Implementation for User Story 5 (after T024 and T025 are RED)

- [x] T026 [US5] Implement `build_projeto(records: list[CsvRecord]) -> ProjetoCompleto` with `_PARSER_REGISTRY` dict in `src/factor_lib/domain/builder.py`
- [x] T027 [US5] Write `tests/integration/domain/conftest.py` — `real_records` fixture that loads CSVs from `data/Projeto_372/` using `factor_lib.export.parse_zip_csv` or direct file read

**Checkpoint**: `pytest tests/unit/domain/test_builder.py tests/integration/domain/` — all GREEN.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Public API, type checking, linting, and documentation.

- [x] T028 Update `src/factor_lib/domain/__init__.py` to re-export: `build_projeto`, `parse_project_info`, `parse_equipe`, `parse_pagamentos`, `parse_plano_trabalho`, `parse_recursos`, `parse_documentos`, `parse_prestacoes_contas`, all 8 dataclass types, `DomainParseError`
- [x] T029 [P] Run `mypy --strict src/factor_lib/domain/` — fix any type errors until clean
- [x] T030 [P] Run `ruff check src/factor_lib/domain/ tests/unit/domain/ tests/integration/domain/` — fix any lint issues
- [x] T031 Run full test suite `pytest tests/unit/domain tests/integration/domain -v` and confirm all GREEN in < 5 seconds
- [x] T032 Validate quickstart.md checklist: `info.referencia == "372"`, `len(equipe) == 19`, `len(pagamentos) == 21`, `len(plano_trabalho) == 185`, Decimal sum correct, no `\xa0` in output

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1–US4 (Phases 3–6)**: Depend on Phase 2; can run in parallel after foundational complete
- **US5 (Phase 7)**: Depends on US1–US4 all complete (builder calls all parsers)
- **Polish (Phase 8)**: Depends on Phase 7

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no story dependencies
- **US2 (P2)**: After Phase 2 — no story dependencies
- **US3 (P3)**: After Phase 2 — no story dependencies
- **US4 (P4)**: After Phase 2 — no story dependencies
- **US5 (P5)**: After US1, US2, US3, US4 all complete

### TDD Within Each Story

1. Write tests → confirm RED
2. Implement → confirm GREEN
3. Proceed to next story

### Parallel Opportunities

- T002–T005: All `__init__.py` files in parallel
- T006–T008: All foundational tests in parallel
- T009–T011: Foundational implementation in parallel (after T006–T008 RED)
- US1–US4 (Phases 3–6): Can run in parallel after Phase 2 complete
- T018–T019: Tests for plano_trabalho and recursos in parallel
- T020–T023: All 4 parser implementations in parallel
- T029–T030: mypy and ruff in parallel

---

## Parallel Example: User Story 4

```bash
# Write tests in parallel (both must be RED):
Task T018: "tests/unit/domain/test_plano_trabalho.py"
Task T019: "tests/unit/domain/test_recursos.py"

# Implement all 4 parsers in parallel (after tests RED):
Task T020: "src/factor_lib/domain/parsers/plano_trabalho.py"
Task T021: "src/factor_lib/domain/parsers/recursos.py"
Task T022: "src/factor_lib/domain/parsers/documentos.py"
Task T023: "src/factor_lib/domain/parsers/prestacao_contas.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational (exceptions + models + utils)
3. Phase 3: US1 — `parse_project_info()`
4. **STOP and VALIDATE**: `parse_project_info()` works on Projeto 372 fixture
5. Proceed to US2 when ready

### Incremental Delivery

1. Setup + Foundational → can import `factor_lib.domain`
2. US1 → `parse_project_info()` works
3. US2 → `parse_equipe()` works
4. US3 → `parse_pagamentos()` works (money as Decimal)
5. US4 → `parse_plano_trabalho()` + `parse_recursos()` work
6. US5 → `build_projeto()` assembles all

---

## Notes

- TDD is NON-NEGOTIABLE: every implementation task must have a preceding failing test
- `\xa0` normalization must be tested explicitly — it is easy to miss
- `Decimal` for all money: never `float`, never `str` in value objects
- Frozen dataclasses: test `FrozenInstanceError` in T007
- Integration test (T025) uses real `data/Projeto_372/` files — no mocking
- All `_source_file` lookups use lowercase basename (e.g., `"equipe.csv"`, not full path)
