# Quickstart: factor_lib.export

**Feature**: 002-csv-export-to-json
**Date**: 2026-05-16

---

## Prerequisites

- feature 001 (`factor_lib` core) installed — see `specs/001-transparency-scraper/quickstart.md`
- `playwright install chromium` already run

---

## Usage

### Full flow (one call)

```python
from playwright.sync_api import sync_playwright
from factor_lib.export import export_project_csv_to_json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to project detail page first (feature 001 handles this)
    page.goto("https://facto.conveniar.com.br/portaltransparencia/")
    # ... click Consultar, click lupa for specific project ...

    result = export_project_csv_to_json(page, "output/project_001.json")
    print(f"{result.total_records} records, {result.files_processed} CSV files.")
    browser.close()
```

### Individual steps

```python
from factor_lib.export import download_csv_export, parse_zip_csv
from factor_lib import save_to_json

# 1. Download ZIP (page must be on detail view)
zip_bytes = download_csv_export(page, timeout=90_000)

# 2. Parse CSV files from ZIP
records = parse_zip_csv(zip_bytes)

# 3. Save to JSON
save_to_json(records, "output/project_001.json")
```

### Output JSON

```json
[
  {
    "Código": "PRJ-001",
    "Situação": "Em andamento",
    "Valor": "500000",
    "_source_file": "projeto_001.csv",
    "_extracted_at": "2026-05-16T14:35:00"
  }
]
```

---

## Run tests (TDD workflow)

```bash
# Step 1: Write test → confirm RED
pytest tests/unit/export/test_downloader.py -v
# Expected: FAILED (before implementation)

# Step 2: Implement → confirm GREEN
pytest tests/unit/export/test_downloader.py -v
# Expected: PASSED

# Full test suite
pytest tests/unit/export tests/integration/export tests/e2e/export

# Type check
mypy src/factor_lib/export/

# Lint
ruff check src/factor_lib/export/ tests/unit/export/
```

---

## Validation Checklist

- [ ] `pytest tests/unit/export` exits 0
- [ ] `pytest tests/integration/export` exits 0
- [ ] `pytest tests/e2e/export` exits 0 (no live portal — uses `page.route()` mock)
- [ ] `mypy --strict src/factor_lib/export/` exits 0
- [ ] `ruff check src/factor_lib/export/` exits 0
- [ ] `export_project_csv_to_json(page, path)` produces valid JSON file
- [ ] Temp dir is deleted after call (check with `tempfile.gettempdir()` before/after)
- [ ] Latin-1 encoded CSV fixture parses without error
- [ ] Empty rows in fixture CSV are excluded from output
