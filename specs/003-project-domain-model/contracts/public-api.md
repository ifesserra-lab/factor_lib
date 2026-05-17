# Public API Contract: factor_lib.domain

**Feature**: 003-project-domain-model
**Date**: 2026-05-16
**Module**: `from factor_lib.domain import ...`

---

## Function: `build_projeto` *(Facade)*

```python
def build_projeto(
    records: list[CsvRecord],
) -> ProjetoCompleto:
    ...
```

**Behaviour**:
1. Groups `records` by normalized `_source_file` field (lowercase basename).
2. Looks up each group in `_PARSER_REGISTRY` → calls matching parser.
3. Unknown `_source_file` values are silently ignored (logged at DEBUG level).
4. Missing sub-entity types (no matching records) → empty tuple in `ProjetoCompleto`.
5. Assembles and returns a frozen `ProjetoCompleto`.

**Errors**:
- `DomainParseError` — `ProjetoInfo` record missing from `records` (required).
- `DomainParseError` — a required field has an invalid value (e.g., bad date format).

---

## Function: `parse_project_info`

```python
def parse_project_info(
    records: list[CsvRecord],
) -> ProjetoInfo:
    ...
```

**Behaviour**:
1. Filters records with `_source_file` matching `"informações do projeto.csv"`.
2. Parses the first matching record into a `ProjetoInfo` value object.
3. Normalizes `referencia` to numeric prefix (e.g., `"372 - ..."` → `"372"`).
4. Parses money fields as `Decimal`; date fields as `datetime.date`.

**Errors**:
- `DomainParseError` — no matching records found.
- `DomainParseError` — required field missing or invalid.

---

## Function: `parse_equipe`

```python
def parse_equipe(
    records: list[CsvRecord],
) -> list[MembroEquipe]:
    ...
```

**Behaviour**:
1. Filters records with `_source_file` matching `"equipe.csv"`.
2. Converts each record to `MembroEquipe`; `\xa0` → `None` for optional fields.
3. `"Sim"` in `Vinculada à inst. executora` → `True`; else → `False`.
4. Returns `[]` if no matching records.

---

## Function: `parse_pagamentos`

```python
def parse_pagamentos(
    records: list[CsvRecord],
) -> list[Pagamento]:
    ...
```

**Behaviour**:
1. Filters records from both payment CSV types (by `_source_file` contains `"pagamento"`).
2. Merges both sources into a single list.
3. `tipo_favorecido` derived from `_source_file`: `"pessoa física"` → `"pessoa_fisica"`,
   otherwise → `"servidor"`.
4. `valor` parsed as `Decimal` from Brazilian format.
5. Returns `[]` if no matching records.

---

## Function: `parse_plano_trabalho`

```python
def parse_plano_trabalho(
    records: list[CsvRecord],
) -> list[ItemPlanoTrabalho]:
    ...
```

**Behaviour**:
1. Filters records with `_source_file` matching `"plano de trabalho.csv"`.
2. Normalizes `\xa0` to `None` in code/optional fields.
3. Parses decimal amount fields as `Decimal("0")` if blank.
4. Returns `[]` if no matching records.

---

## Function: `parse_recursos`

```python
def parse_recursos(
    records: list[CsvRecord],
) -> list[RecursoRubrica]:
    ...
```

**Behaviour**: Filters `"recursos por rubrica receita separada.csv"` records; parses
`aprovado`, `liberado`, `executado` as `Decimal`. Returns `[]` if none.

---

## Data Classes

### `ProjetoInfo`

```python
@dataclass(frozen=True)
class ProjetoInfo:
    referencia: str
    coordenador: str
    financiadora: str
    data_inicio: datetime.date
    data_vigencia: datetime.date
    data_encerramento: datetime.date | None
    tipo: str
    instituicao_executora: str
    departamento: str | None
    processo: str | None
    valor_aprovado: Decimal
    objetivo: str
```

### `MembroEquipe`

```python
@dataclass(frozen=True)
class MembroEquipe:
    referencia: str
    nome: str
    funcao: str
    instituicao: str | None
    vinculo: str | None
    grau_instrucao: str | None
    carga_horaria: str | None
    vinculada_executora: bool
```

### `Pagamento`

```python
@dataclass(frozen=True)
class Pagamento:
    referencia: str
    cpf: str
    nome_favorecido: str
    tipo_pagamento: str
    data_pagamento: datetime.date
    mes_competencia: str
    valor: Decimal
    tipo_favorecido: str    # "pessoa_fisica" | "servidor"
```

### `ItemPlanoTrabalho`

```python
@dataclass(frozen=True)
class ItemPlanoTrabalho:
    referencia: str
    agrupamento: str | None
    rubrica: str
    codigo: str | None
    produto: str | None
    descricao: str | None
    justificativa: str | None
    qtde_aprovada: str | None
    valor_unitario: Decimal | None
    valor_total_aprovado: Decimal
    valor_executado: Decimal
```

### `RecursoRubrica`

```python
@dataclass(frozen=True)
class RecursoRubrica:
    referencia: str
    tipo_rubrica: str
    rubrica: str
    aprovado: Decimal
    liberado: Decimal
    executado: Decimal
    moeda: str
```

### `Documento`

```python
@dataclass(frozen=True)
class Documento:
    referencia: str
    titulo: str
    descricao: str | None
```

### `PrestacaoContas`

```python
@dataclass(frozen=True)
class PrestacaoContas:
    referencia: str
    titulo: str
    descricao: str | None
    data_inicio: datetime.date
    data_final: datetime.date
```

### `ProjetoCompleto`

```python
@dataclass(frozen=True)
class ProjetoCompleto:
    info: ProjetoInfo
    equipe: tuple[MembroEquipe, ...]
    documentos: tuple[Documento, ...]
    pagamentos: tuple[Pagamento, ...]
    plano_trabalho: tuple[ItemPlanoTrabalho, ...]
    recursos: tuple[RecursoRubrica, ...]
    prestacoes_contas: tuple[PrestacaoContas, ...]
```

### Exception

```python
class DomainParseError(FactoLibError):
    field: str     # name of the field that caused the error
    reason: str    # human-readable explanation
```
