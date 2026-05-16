# Public API Contract: factor_lib

**Feature**: 001-transparency-scraper
**Date**: 2026-05-16
**Type**: Python library public interface

---

## Module: `factor_lib`

All public symbols re-exported from `factor_lib/__init__.py`.

---

## Function: `list_projects`

```python
def list_projects(
    url: str = "https://facto.conveniar.com.br/portaltransparencia/",
    *,
    headless: bool = True,
    timeout: int = 30_000,
) -> list[ProjectListingRecord]:
    ...
```

**Behaviour**:
1. Launches a Chromium browser (headless by default).
2. Navigates to `url`.
3. Clicks the "Consultar" button and waits for the project listing to render.
4. Extracts all project rows (all pages if paginated).
5. Returns list of `ProjectListingRecord`. Returns `[]` if no projects found.

**Errors**:
- Raises `PortalNavigationError` if the "Consultar" button cannot be found within
  `timeout` milliseconds.
- Raises `PortalNavigationError` if navigation to `url` fails.

---

## Function: `scrape_all_projects`

```python
def scrape_all_projects(
    url: str = "https://facto.conveniar.com.br/portaltransparencia/",
    *,
    headless: bool = True,
    timeout: int = 30_000,
) -> ScrapeResult:
    ...
```

**Behaviour**:
1. Calls `list_projects(url, headless=headless, timeout=timeout)` internally.
2. For each `ProjectListingRecord`, clicks its lupa icon and scrapes the detail view.
3. On per-project failure: logs error, sets `_error` on the record, continues.
4. Returns a `ScrapeResult` with all records and summary metadata.

**Errors**:
- Raises `PortalNavigationError` if the initial listing cannot be loaded.
- Per-project errors do NOT raise; they are captured in `ProjectDetailRecord._error`.

---

## Function: `save_to_json`

```python
def save_to_json(
    records: list[ProjectDetailRecord] | ScrapeResult,
    path: str | os.PathLike,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    ...
```

**Behaviour**:
1. Accepts either a list of `ProjectDetailRecord` or a `ScrapeResult` (extracts
   `.records` automatically).
2. Creates all parent directories of `path` if they do not exist.
3. Writes a JSON array of serialized records to `path`, overwriting any existing file.
4. Each record is serialized as a flat JSON object (fields merged into root).

**Errors**:
- Raises `OSError` if the file cannot be written (permissions, disk full, etc.).

---

## Function: `scrape_and_save` *(high-level facade)*

```python
def scrape_and_save(
    output_path: str | os.PathLike,
    url: str = "https://facto.conveniar.com.br/portaltransparencia/",
    *,
    headless: bool = True,
    timeout: int = 30_000,
    indent: int = 2,
) -> ScrapeResult:
    ...
```

**Behaviour**:
1. Calls `scrape_all_projects(url, headless=headless, timeout=timeout)`.
2. Calls `save_to_json(result, output_path, indent=indent)`.
3. Returns the `ScrapeResult`.

**Errors**:
- Propagates `PortalNavigationError` from `scrape_all_projects`.
- Propagates `OSError` from `save_to_json`.

---

## Exceptions

```python
class FactoLibError(Exception):
    """Base exception for all factor_lib errors."""

class PortalNavigationError(FactoLibError):
    """Raised when browser automation cannot find or interact with a portal element."""
```

---

## Data Classes

### `ProjectListingRecord`

```python
@dataclass(frozen=True)
class ProjectListingRecord:
    id: str
    name: str
    raw_row: dict[str, str]
```

### `ProjectDetailRecord`

```python
@dataclass(frozen=True)
class ProjectDetailRecord:
    id: str
    name: str
    fields: dict[str, str]
    _source_url: str
    _scraped_at: str          # ISO 8601
    _error: str | None = None
```

### `ScrapeResult`

```python
@dataclass(frozen=True)
class ScrapeResult:
    records: tuple[ProjectDetailRecord, ...]
    total: int
    success_count: int
    error_count: int
    started_at: str           # ISO 8601
    completed_at: str         # ISO 8601
```

---

## Usage Example

```python
from factor_lib import scrape_and_save

result = scrape_and_save("output/projects.json")
print(f"Scraped {result.success_count} projects, {result.error_count} errors.")
```
