# Research: Structured Project Domain Model

**Feature**: 003-project-domain-model
**Date**: 2026-05-16

---

## Decision 1: Decimal for Brazilian Money Strings

**Decision**: Use Python stdlib `decimal.Decimal` for all monetary amounts. Parse
Brazilian format (`3.722.800,00`) by stripping dots and replacing comma with period
before constructing `Decimal`.

```python
from decimal import Decimal

def _parse_money(value: str) -> Decimal:
    clean = _clean(value)
    if clean is None:
        return Decimal("0")
    return Decimal(clean.replace(".", "").replace(",", "."))
```

**Rationale**: `float` loses precision for large government amounts (e.g., R$ 3.7M
with 2 decimal places). `Decimal` guarantees exact representation. Constitution §IV
forbids magic number pitfalls — `Decimal` is the canonical choice for financial data.

**Alternatives considered**:
- `float`: rejected — precision loss; `3722800.00` may not round-trip correctly.
- Store as string: rejected — prevents aggregation (sum, compare) without re-parsing.
- `fractions.Fraction`: rejected — overkill; no fractional-cent amounts expected.

---

## Decision 2: Router/Registry Pattern for CSV Type Dispatch

**Decision**: Use a `_PARSER_REGISTRY: dict[str, Callable]` mapping normalized CSV
filename (lowercase basename, no path) to parser function. The `build_projeto`
facade looks up each record's `_source_file` in the registry.

```python
_PARSER_REGISTRY: dict[str, str] = {
    "equipe.csv": "equipe",
    "documentos.csv": "documentos",
    "pagamento de pessoa física.csv": "pagamentos",
    "pagamento de servidores ou agentes públicos.csv": "pagamentos",
    "informações do projeto.csv": "projeto_info",
    "plano de trabalho.csv": "plano_trabalho",
    "prestação de contas.csv": "prestacao_contas",
    "recursos por rubrica receita separada.csv": "recursos",
}
```

**Rationale**: Decouples routing logic from parsing logic. Multiple CSV filenames can
map to the same parser (e.g., both payment CSVs share `parse_pagamentos`). Open/Closed
Principle (§III) — adding a new CSV type only requires registering a new key, no
modification to `build_projeto`. Avoids a God Object (§IV).

**Alternatives considered**:
- `if/elif` chain in `build_projeto`: rejected — becomes God Method as new CSV types added.
- ABC `CsvParser` strategy: rejected for v1 — one parser per type; ABC overhead unjustified.
- Match on CSV column headers (content-based routing): rejected — fragile; portal may
  change column names without changing file names.

---

## Decision 3: Non-Breaking Space (`\xa0`) Normalization

**Decision**: Apply `_clean(value: str | None) -> str | None` helper to all fields.
Returns `None` if value is `None`, empty, or contains only `\xa0`; returns stripped
string otherwise.

```python
_EMPTY = {None, "", "\xa0", " "}

def _clean(value: str | None) -> str | None:
    if value is None or value.strip() in _EMPTY or value.strip() == "\xa0":
        return None
    return value.strip()
```

**Rationale**: The real portal data uses `\xa0` (Latin-1 non-breaking space, 0xA0) as
a null placeholder throughout `Plano de trabalho.csv` (code fields) and `Equipe.csv`
(carga horária). Leaving it as-is causes silent downstream errors and violates the
principle that domain objects carry only meaningful data.

**Alternatives considered**:
- Store `\xa0` as-is: rejected — downstream `sum()`, string comparisons fail silently.
- Replace with `""`: rejected — empty string and absent value are semantically different
  for optional fields.

---

## Decision 4: Date String Parsing

**Decision**: Parse `DD/MM/YYYY` date strings to `datetime.date` using
`datetime.strptime(value, "%d/%m/%Y").date()`. Optional date fields return `None`
on blank/`\xa0` input. Invalid format raises `ParseError`.

**Rationale**: Typed dates enable sorting and range queries without string gymnastics.
Brazilian portal consistently uses `DD/MM/YYYY`. `datetime.date` is stdlib, no deps.

**Alternatives considered**:
- Store dates as strings: rejected — prevents date arithmetic, sorting.
- `dateutil.parser.parse`: rejected — adds a dependency; `strptime` with explicit
  format is safer for a known format.

---

## Decision 5: Module Structure — Sub-Package of Parsers

**Decision**: Create `src/factor_lib/domain/parsers/` as a sub-package with one
module per entity type (`equipe.py`, `pagamentos.py`, etc.). Root `builder.py`
composes all parsers.

```
src/factor_lib/domain/
├── __init__.py
├── models.py         # all value objects (frozen dataclasses)
├── builder.py        # build_projeto() — Facade
├── exceptions.py     # DomainParseError
└── parsers/
    ├── __init__.py
    ├── _utils.py     # _clean(), _parse_money(), _parse_date()
    ├── projeto_info.py
    ├── equipe.py
    ├── pagamentos.py
    ├── plano_trabalho.py
    ├── recursos.py
    ├── documentos.py
    └── prestacao_contas.py
```

**Rationale**: Single Responsibility (§III SOLID S) — each parser file has one reason
to change. Prevents God Module. Matches the 8-CSV structure of the portal export
(one module per entity type). Easy to add new CSV types in v2.

**Alternatives considered**:
- Single `parsers.py`: rejected — would grow to 400+ lines; violates SRP.
- One ABC `CsvParser` per type with a class: rejected — pure functions are sufficient
  for stateless parsers; class hierarchy adds overhead without benefit.

---

## Decision 6: `ProjetoCompleto` — Aggregate Root

**Decision**: `ProjetoCompleto` is the root aggregate containing all sub-entities.
`build_projeto(records: list[CsvRecord]) -> ProjetoCompleto` is the single entry point
(Facade pattern per §III). The function:
1. Groups records by `_source_file` → parser lookup
2. Calls each applicable parser
3. Assembles `ProjetoCompleto`
4. Missing sub-entity types → empty list (not error)

**Rationale**: Facade pattern (§III) — callers get one function, one return type.
`ProjetoCompleto` acts as a Value Object aggregate (§III) — immutable, self-contained.
Missing sub-entities default to empty lists per FR-007 and US5 acceptance scenario 2.

**Alternatives considered**:
- Return `dict[str, list]`: rejected — untyped, violates constitution §II (type hints
  on all public interfaces).
- Separate `build_*` functions per entity: rejected — forces callers to manage
  8 separate calls; Facade exists precisely to prevent this.
