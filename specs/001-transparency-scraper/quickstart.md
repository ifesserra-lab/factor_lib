# Quickstart: factor_lib

**Feature**: 001-transparency-scraper
**Date**: 2026-05-16

---

## Prerequisites

- Python 3.11+
- Git

---

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd factor_lib

# Install with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

---

## Run a full scrape

```python
from factor_lib import scrape_and_save

result = scrape_and_save("output/projects.json")
print(f"Done — {result.success_count} scraped, {result.error_count} errors.")
```

Output file `output/projects.json` will contain a JSON array like:

```json
[
  {
    "id": "PRJ-001",
    "name": "Projeto Exemplo",
    "Situação": "Em andamento",
    "Valor Total": "R$ 500.000,00",
    "_source_url": "https://facto.conveniar.com.br/portaltransparencia/",
    "_scraped_at": "2026-05-16T14:30:00",
    "_error": null
  }
]
```

---

## Run tests

```bash
# Unit + integration tests
pytest tests/unit tests/integration

# E2E tests (uses recorded fixtures — no live portal required)
pytest tests/e2e

# All tests
pytest

# Type check
mypy src/

# Lint
ruff check src/ tests/
```

---

## TDD Workflow (per constitution)

1. Write a failing test in the appropriate `tests/` directory.
2. Run `pytest` and confirm it fails (Red).
3. Write the minimum implementation to make it pass (Green).
4. Refactor; keep tests green.
5. Commit test and implementation in separate commits.

---

## Validation Checklist

- [ ] `pytest` exits 0 (all tests green)
- [ ] `mypy src/` exits 0 (no type errors)
- [ ] `ruff check src/ tests/` exits 0 (no lint warnings)
- [ ] `scrape_and_save("output/projects.json")` produces a valid JSON file
- [ ] JSON file contains one entry per project visible on the portal
- [ ] Each entry with a successful scrape has no `_error` field (or `_error: null`)
