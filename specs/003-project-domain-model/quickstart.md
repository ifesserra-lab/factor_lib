# Quickstart: factor_lib.domain

**Feature**: 003-project-domain-model
**Date**: 2026-05-16

---

## Prerequisites

- Features 001 and 002 installed — see `specs/002-csv-export-to-json/quickstart.md`
- `data/Projeto_372/` available as fixture for integration tests

---

## Usage

### Full flow — from portal export to structured domain object

```python
from playwright.sync_api import sync_playwright
from factor_lib.export import export_project_csv_to_json
from factor_lib.domain import build_projeto
from factor_lib.export import parse_zip_csv, download_csv_export

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to detail page (feature 001 handles this)
    page.goto("https://facto.conveniar.com.br/portaltransparencia/")
    # ... click Buscar → click Detalhes for target project ...

    # Download and parse CSV export (feature 002)
    zip_bytes = download_csv_export(page)
    records = parse_zip_csv(zip_bytes)

    # Build structured domain model (feature 003)
    projeto = build_projeto(records)

    print(f"Projeto {projeto.info.referencia}: {projeto.info.objetivo[:60]}...")
    print(f"Equipe: {len(projeto.equipe)} membros")
    print(f"Pagamentos: {len(projeto.pagamentos)} registros")
    print(f"Valor aprovado: R$ {projeto.info.valor_aprovado:,.2f}")

    browser.close()
```

### Using individual parsers

```python
from factor_lib.domain import parse_project_info, parse_equipe, parse_pagamentos

# records is list[CsvRecord] from parse_zip_csv()
info = parse_project_info(records)
equipe = parse_equipe(records)
pagamentos = parse_pagamentos(records)

# Financial summary
total_pago = sum(p.valor for p in pagamentos)
print(f"Total pago: R$ {total_pago:,.2f}")
print(f"Coordenados por: {info.coordenador}")
```

### Integration with JSON output

```python
import json
from factor_lib.domain import build_projeto
from factor_lib.serializers import save_to_json

projeto = build_projeto(records)

# Save all payments as JSON
save_to_json(list(projeto.pagamentos), "output/pagamentos_372.json")

# ProjetoCompleto as dict (for serialization)
from dataclasses import asdict
from decimal import Decimal
import datetime

def json_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError(f"Non-serializable: {type(obj)}")

with open("output/projeto_372.json", "w") as f:
    json.dump(asdict(projeto), f, default=json_default, indent=2, ensure_ascii=False)
```

---

## Run tests (TDD workflow)

```bash
# Step 1: Write test → confirm RED
pytest tests/unit/domain/test_parsers.py -v
# Expected: FAILED (before implementation)

# Step 2: Implement → confirm GREEN
pytest tests/unit/domain/test_parsers.py -v
# Expected: PASSED

# Full test suite
pytest tests/unit/domain tests/integration/domain

# Type check
mypy --strict src/factor_lib/domain/

# Lint
ruff check src/factor_lib/domain/ tests/unit/domain/ tests/integration/domain/
```

---

## Validation Checklist

- [ ] `pytest tests/unit/domain` exits 0
- [ ] `pytest tests/integration/domain` exits 0
- [ ] `mypy --strict src/factor_lib/domain/` exits 0
- [ ] `ruff check src/factor_lib/domain/` exits 0
- [ ] `build_projeto(records)` on Projeto 372 fixture: `len(equipe) == 19`, `len(pagamentos) == 21`, `len(plano_trabalho) == 185`
- [ ] `sum(p.valor for p in projeto.pagamentos)` returns correct `Decimal` (no float)
- [ ] `\xa0` fields return `None` (not the string `"\xa0"`)
- [ ] `info.data_inicio` is `datetime.date`, not `str`
