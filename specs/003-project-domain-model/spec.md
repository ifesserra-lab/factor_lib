# Feature Specification: Structured Project Domain Model

**Feature Branch**: `003-project-domain-model`
**Created**: 2026-05-16
**Status**: Draft
**Input**: User description: "analise a pasta data/Projeto_372/ para entender o modelo de dados"
**Data source**: `data/Projeto_372/` — real export from Facto portal (8 CSV files, project #372)

## Data Model Analysis

Analysis of the 8 CSV files exported from project #372 reveals the following entity schema:

| CSV File | Entidade | Colunas | Linhas (Projeto 372) |
|----------|----------|---------|----------------------|
| `Informações do projeto.csv` | ProjetoInfo | 12 | 1 |
| `Equipe.csv` | MembroEquipe | 8 | 19 |
| `Documentos.csv` | Documento | 3 | 1 |
| `Pagamento de pessoa física.csv` | Pagamento | 7 | 5 |
| `Pagamento de servidores ou agentes públicos.csv` | Pagamento | 7 | 16 |
| `Plano de trabalho.csv` | ItemPlanoTrabalho | 11 | 185 |
| `Prestação de contas.csv` | PrestacaoContas | 5 | 1 |
| `Recursos por rubrica receita separada.csv` | RecursoRubrica | 7 | 11 |

**Key observations**:
- All CSVs use `|` as delimiter.
- All CSVs share `Referência do projeto` as the join key.
- Encoding: mix of UTF-8 and Latin-1 (as handled by feature 002).
- Money values use Brazilian format: `3.722.800,00` (dots = thousand, comma = decimal).
- Dates use `DD/MM/YYYY` format.
- CPF values are masked: `***.506.767-**`.
- Some fields use `\xa0` (non-breaking space) as a null placeholder.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse Project Info (Priority: P1)

A developer provides a list of `CsvRecord` (from feature 002) and calls
`parse_project_info(records)` to extract the core project metadata into a
`ProjetoInfo` value object with typed fields.

**Why this priority**: The `ProjetoInfo` entity is the root anchor for all
other entities. Without it, no structured domain model can be assembled.
Demonstrates the core mapping pattern for all other parsers.

**Independent Test**: Call `parse_project_info(records)` with records sourced
from `Informações do projeto.csv` fixture and assert all 12 fields are populated
with correct types.

**Acceptance Scenarios**:

1. **Given** a list of CsvRecord from `Informações do projeto.csv`, **When**
   `parse_project_info(records)` is called, **Then** returns a `ProjetoInfo`
   with `referencia`, `coordenador`, `financiadora`, `data_inicio`,
   `data_vigencia`, `valor_aprovado`, and `objetivo` populated.
2. **Given** an empty record list, **When** `parse_project_info` is called,
   **Then** raises `ParseError` with a message indicating no project info found.
3. **Given** records with missing optional fields (e.g., `data_encerramento`),
   **When** parsed, **Then** missing optional fields default to `None` without
   raising an error.

---

### User Story 2 - Parse Team Members (Priority: P2)

A developer calls `parse_equipe(records)` to extract the team members list
from `Equipe.csv` records, returning a list of `MembroEquipe` value objects
with role, institution, and education level.

**Why this priority**: Team data is the most frequently queried sub-entity
(19 members in a typical project). It enables staffing and cost analysis.

**Independent Test**: Call `parse_equipe(records)` with records from
`Equipe.csv` fixture and assert correct count, roles, and institution names.

**Acceptance Scenarios**:

1. **Given** records from `Equipe.csv`, **When** `parse_equipe(records)` is
   called, **Then** returns a list of `MembroEquipe` with `nome`, `funcao`,
   `instituicao`, and `vinculada_executora` set correctly.
2. **Given** records with `Vinculada à inst. executora` = "Sim", **When**
   parsed, **Then** `vinculada_executora` is `True`; "Não" maps to `False`.
3. **Given** an empty record list, **When** parsed, **Then** returns `[]`
   without raising an error.

---

### User Story 3 - Parse Financial Data (Priority: P3)

A developer calls `parse_pagamentos(records)` to merge payments from both
`Pagamento de pessoa física.csv` and `Pagamento de servidores ou agentes públicos.csv`
into a unified list of `Pagamento` value objects with typed amounts (Decimal).

**Why this priority**: Payment data is the financially sensitive core of the
portal. Typed amounts (Decimal, not string) allow accurate aggregation and
reporting. Two separate CSV sources must be unified.

**Independent Test**: Call `parse_pagamentos(records)` with fixture records
from both payment CSVs and assert total count = 21, each record has a parsed
Decimal `valor`.

**Acceptance Scenarios**:

1. **Given** records from both payment CSVs, **When** `parse_pagamentos(records)`
   is called, **Then** returns a unified list of `Pagamento` regardless of
   source CSV type.
2. **Given** a `Pagamento` record, **When** accessing `valor`, **Then** it is
   a `Decimal` (not string); Brazilian money format `3.722.800,00` parses to
   `Decimal("3722800.00")`.
3. **Given** records with masked CPF (`***.506.767-**`), **When** parsed,
   **Then** CPF is stored as-is (no unmasking attempted).

---

### User Story 4 - Parse Work Plan and Resources (Priority: P4)

A developer calls `parse_plano_trabalho(records)` and `parse_recursos(records)` to
extract the 185-line work plan and the 11 budget-by-rubrica resource records,
each with typed amounts for approved, executed, and unit values.

**Why this priority**: The work plan is the largest dataset (185 rows) and
drives budget tracking. Resources give the high-level financial summary by
category. Both needed for any financial dashboard.

**Independent Test**: Call `parse_plano_trabalho(records)` with fixture records
and assert count = 185, each `ItemPlanoTrabalho` has `rubrica`, `produto`,
`valor_total_aprovado` as Decimal.

**Acceptance Scenarios**:

1. **Given** records from `Plano de trabalho.csv`, **When**
   `parse_plano_trabalho(records)` is called, **Then** returns list of
   `ItemPlanoTrabalho` with `rubrica`, `codigo`, `produto`, `valor_total_aprovado`,
   `valor_executado` populated.
2. **Given** records where `\xa0` (non-breaking space) appears in code or value
   fields, **When** parsed, **Then** `\xa0` is normalized to `None` or `""`.
3. **Given** records from `Recursos por rubrica receita separada.csv`, **When**
   `parse_recursos(records)` is called, **Then** returns list of `RecursoRubrica`
   with `tipo_rubrica`, `rubrica`, `aprovado`, `executado` as Decimal.

---

### User Story 5 - Assemble ProjetoCompleto (Priority: P5)

A developer calls `build_projeto(records)` with the full list of `CsvRecord`
from a single project's ZIP export (all 8 CSV types merged), and receives
a `ProjetoCompleto` value object containing all sub-entities.

**Why this priority**: The facade that composes all parsers into a single call.
Enables downstream consumers to work with one structured object instead of
8 separate lists.

**Independent Test**: Call `build_projeto(records)` with all records from
`data/Projeto_372/` fixture and assert `ProjetoCompleto` contains correct
counts for each sub-entity.

**Acceptance Scenarios**:

1. **Given** a full list of `CsvRecord` from all 8 CSV files, **When**
   `build_projeto(records)` is called, **Then** returns a `ProjetoCompleto`
   with `info`, `equipe`, `documentos`, `pagamentos`, `plano_trabalho`,
   `recursos`, and `prestacoes_contas` all populated.
2. **Given** a list with only some CSV types present, **When** `build_projeto`
   is called, **Then** missing sub-entities default to empty lists without
   raising an error.

---

### Edge Cases

- `\xa0` (non-breaking space) used as null placeholder in several fields — must be normalized.
- Brazilian money strings (`3.722.800,00`) must parse to `Decimal`, not `float` (precision).
- Date strings (`07/04/2026`) must parse to `datetime.date` — invalid dates should surface clearly.
- CSV files use `|` as delimiter; comma-delimited fields must not be mis-parsed.
- Project reference string (`372 - Estudos de Impacto...`) is long and repeated in every row — normalization to just `"372"` is acceptable for the reference key.
- Pagamentos from two different CSVs share the same schema but different `_source_file` tags — both must be recognized as payment records.
- Records with all-empty fields (empty rows from feature 002 parser) are already filtered; no double-filtering needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Library MUST parse `Informações do projeto` records into a typed
  `ProjetoInfo` value object with 12 fields; missing optional fields MUST default
  to `None`.
- **FR-002**: Library MUST parse `Equipe` records into a list of `MembroEquipe`
  value objects; `Vinculada à inst. executora` MUST be converted to `bool`.
- **FR-003**: Library MUST parse both payment CSV types (`pessoa física` and
  `servidores`) into a unified `list[Pagamento]`; `valor` MUST be `Decimal`.
- **FR-004**: Library MUST parse `Plano de trabalho` into `list[ItemPlanoTrabalho]`;
  `valor_total_aprovado` and `valor_executado` MUST be `Decimal`; `\xa0` MUST
  normalize to `None`.
- **FR-005**: Library MUST parse `Recursos por rubrica` into `list[RecursoRubrica]`;
  `aprovado`, `liberado`, `executado` MUST be `Decimal`.
- **FR-006**: Library MUST parse `Documentos` and `Prestação de contas` into
  their respective value objects; dates MUST be `datetime.date`.
- **FR-007**: Library MUST assemble all sub-entities into a single `ProjetoCompleto`
  value object via `build_projeto(records: list[CsvRecord])`.
- **FR-008**: Library MUST route records to correct parsers by inspecting
  `_source_file` field (CSV filename used as discriminator).
- **FR-009**: Brazilian money strings MUST be converted to `Decimal` without
  `float` intermediate to preserve precision.
- **FR-010**: All value objects MUST be frozen dataclasses (immutable).

### Key Entities

- **ProjetoInfo**: Core project metadata — coordinator, funder, dates, approved amount, objective.
- **MembroEquipe**: Team member — name, role (function), institution, education level, workload, linked-to-executor flag.
- **Pagamento**: Payment record — masked CPF, beneficiary name, payment type, date, reference month, amount (Decimal). Covers both `pessoa física` and `servidor` categories.
- **ItemPlanoTrabalho**: Work plan line item — grouping, budget category (rubrica), code, product, description, approved quantity/amount, executed amount.
- **RecursoRubrica**: Budget summary by category — type (expense/income), rubrica name, approved/released/executed amounts, currency.
- **Documento**: Attached document — title, description.
- **PrestacaoContas**: Accountability report — title, description, reporting period.
- **ProjetoCompleto**: Root aggregate — contains ProjetoInfo + all sub-entity lists.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `build_projeto(records)` on the 239 real records from `data/Projeto_372/`
  produces a `ProjetoCompleto` with `info.referencia == "372"`, `len(equipe) == 19`,
  `len(pagamentos) == 21`, `len(plano_trabalho) == 185`, `len(recursos) == 11`.
- **SC-002**: All monetary `Decimal` values in `ProjetoCompleto` sum correctly —
  `sum(r.valor for r in pagamentos)` matches the sum computed from the raw CSV strings.
- **SC-003**: No data is lost — total record count across all sub-entities equals
  total input `CsvRecord` count (239 records).
- **SC-004**: All parsers pass `mypy --strict`; no `Any` fields in value objects
  except where explicitly justified.
- **SC-005**: Full test suite (unit + integration) runs in under 5 seconds with
  no live portal access (fixture-based).

## Assumptions

- The `_source_file` field in each `CsvRecord` (set by feature 002) is the
  discriminator used to route records to the correct parser. Filenames are
  assumed to follow the fixed naming convention used by the Facto portal.
- All projects share the same 8-CSV export structure. Different projects may
  have more or fewer rows but the same column schema.
- Money values use Brazilian decimal format (`1.234,56` = `1234.56`). No
  currency conversion is performed; amounts are preserved in their original
  currency (BRL assumed).
- Date strings use `DD/MM/YYYY` format throughout.
- `\xa0` (Latin-1 non-breaking space, hex 0xA0) is used as a null/empty
  placeholder in several fields and must be treated as absent data.
- This feature is packaged inside `factor_lib` as `factor_lib.domain` module,
  reusing `CsvRecord` from `factor_lib.export`.
- The caller (e.g., `export_project_csv_to_json`) provides the raw
  `list[CsvRecord]`; this feature does not handle download or parsing of ZIP.
- Parallel processing across multiple projects is out of scope for v1.
