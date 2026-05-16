# Public API Contract: factor_lib.export

**Feature**: 002-csv-export-to-json
**Date**: 2026-05-16
**Module**: `from factor_lib.export import ...`

---

## Function: `download_csv_export`

```python
def download_csv_export(
    page: playwright.sync_api.Page,
    *,
    timeout: int = 60_000,
) -> bytes:
    ...
```

**Behaviour**:
1. Locates "Exportar em CSV" button on the current page.
2. Uses `page.expect_download(timeout=timeout)` to intercept the download.
3. Clicks the button; Playwright follows any redirect automatically.
4. Saves ZIP to a `TemporaryDirectory`; reads bytes; deletes temp dir.
5. Returns ZIP content as `bytes`.

**Errors**:
- `ButtonNotFoundError` — button not found within default selector timeout.
- `DownloadTimeoutError` — download not complete within `timeout` milliseconds.

---

## Function: `parse_zip_csv`

```python
def parse_zip_csv(
    zip_bytes: bytes,
) -> list[CsvRecord]:
    ...
```

**Behaviour**:
1. Opens ZIP from `zip_bytes` in memory (`io.BytesIO`).
2. Enumerates all members ending in `.csv`; ignores non-CSV files silently.
3. For each CSV: tries UTF-8 decode; falls back to Latin-1 on `UnicodeDecodeError`.
4. Parses with `csv.DictReader`; skips empty rows (debug-level log of count).
5. Rows shorter than headers: missing columns default to `""`.
6. Tags each record: `_source_file=<csv_name>`, `_extracted_at=<ISO 8601 now>`.
7. Returns flat `list[CsvRecord]` (all CSVs merged).

**Errors**:
- `ParseError` — ZIP is corrupt or a CSV fails both UTF-8 and Latin-1 decoding.
- Returns `[]` (empty list) if ZIP contains no CSV files (no exception raised).

---

## Function: `export_project_csv_to_json` *(Facade)*

```python
def export_project_csv_to_json(
    page: playwright.sync_api.Page,
    output_path: str | os.PathLike,
    *,
    timeout: int = 60_000,
    indent: int = 2,
) -> ExportResult:
    ...
```

**Behaviour**:
1. Calls `download_csv_export(page, timeout=timeout)` → ZIP bytes.
2. Calls `parse_zip_csv(zip_bytes)` → list of `CsvRecord`.
3. Calls `save_to_json(records, output_path, indent=indent)` (reused from core).
4. Returns `ExportResult` with records and summary metadata.
5. Each stage wrapped in try/except; re-raised as `ExportError(f"<stage> stage failed: {e}")`.

**Errors**:
- `ExportError` with `stage` attribute indicating where failure occurred:
  - `"download"` — download failed or timed out.
  - `"parse"` — ZIP or CSV parsing failed.
  - `"save"` — JSON file could not be written.
- `OSError` propagated from `save_to_json` for filesystem errors.

---

## Data Classes

### `CsvRecord`

```python
@dataclass(frozen=True)
class CsvRecord:
    fields: dict[str, str]
    _source_file: str
    _extracted_at: str     # ISO 8601
```

### `ExportResult`

```python
@dataclass(frozen=True)
class ExportResult:
    records: tuple[CsvRecord, ...]
    total_records: int
    files_processed: int
    errors: tuple[str, ...]
    exported_at: str       # ISO 8601
```

### Exceptions

```python
class ExportError(FactoLibError):
    stage: str    # "download" | "parse" | "save"
    reason: str

class DownloadTimeoutError(ExportError): ...
class ButtonNotFoundError(ExportError): ...
class ParseError(ExportError): ...
```

---

## Usage Examples

```python
# Full flow — one call
from factor_lib.export import export_project_csv_to_json

result = export_project_csv_to_json(page, "output/project_001.json")
print(f"{result.total_records} records from {result.files_processed} CSV files.")

# Individual steps
from factor_lib.export import download_csv_export, parse_zip_csv
from factor_lib import save_to_json

zip_bytes = download_csv_export(page, timeout=90_000)
records = parse_zip_csv(zip_bytes)
save_to_json(records, "output/project_001.json")
```
