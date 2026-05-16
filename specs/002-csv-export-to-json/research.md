# Research: CSV Export to JSON Processor

**Feature**: 002-csv-export-to-json
**Date**: 2026-05-16

---

## Decision 1: ZIP and CSV Parsing — stdlib only

**Decision**: Use Python stdlib `zipfile.ZipFile` and `csv.DictReader`. Zero new dependencies.

**Rationale**: `zipfile` and `csv` are battle-tested stdlib modules. Adding a third-party
library (e.g., `pandas`) for this simple use case violates YAGNI and adds install
overhead. Constitution §II mandates justification for new dependencies.

**Alternatives considered**:
- `pandas.read_csv`: rejected — heavyweight; overkill for key-value row extraction.
- `openpyxl`: rejected — only needed if portal exports XLSX; ZIP+CSV is stated assumption.

---

## Decision 2: Temp Dir Lifecycle — context manager

**Decision**: `tempfile.TemporaryDirectory()` as context manager in `downloader.py`.
Cleanup guaranteed via `__exit__` regardless of success or failure.

**Rationale**: Clarification Q1 mandated library-managed temp dir with auto-delete.
`TemporaryDirectory` as context manager is the Python-idiomatic pattern (constitution §II).
`try/finally` wrapping would also work but is more verbose.

**Alternatives considered**:
- `tempfile.mkdtemp()` + manual `shutil.rmtree()`: rejected — cleanup not guaranteed on exception.
- Caller-provided path: rejected per clarification Q1.

---

## Decision 3: Playwright Download Event Handling

**Decision**: Use `page.expect_download()` context manager to intercept the download
triggered by clicking "Exportar em CSV". Save to temp dir. `timeout=60_000` (60s, per
clarification Q2).

**Rationale**: `expect_download()` is the official Playwright API for file downloads.
It handles both direct downloads and redirect-triggered downloads transparently — satisfying
clarification Q4 (follow redirect automatically).

**Alternatives considered**:
- Polling `page.route()` for download URL: rejected — fragile; doesn't work for all server
  configurations.
- `request.get()` with session cookies: rejected — requires auth token extraction; brittle.

---

## Decision 4: Encoding Fallback — UTF-8 → Latin-1

**Decision**: Try `utf-8` decode first; on `UnicodeDecodeError` retry with `latin-1`
(ISO-8859-1). If Latin-1 also fails, raise `ExportError`.

**Rationale**: Brazilian government systems historically use Latin-1. UTF-8 is the modern
default. The two-step fallback covers both without guessing upfront. Clarification Q3
approved silent skip of empty rows with debug log.

**Alternatives considered**:
- `chardet` auto-detection: rejected — extra dependency; overkill for two-encoding case.
- Always assume Latin-1: rejected — breaks correctly encoded UTF-8 files.

---

## Decision 5: Strategy Pattern for CSV Parser

**Decision**: `csv_parser.py` implements a pure function `parse_zip_csv(zip_bytes)` as
the Strategy interface. No ABC needed at v1 — the function signature IS the contract.
Can be promoted to ABC if multiple portal export formats need to be supported in v2.

**Rationale**: Constitution §III requires Strategy where algorithms are interchangeable.
A module-level function is the minimal viable Strategy for a single implementation.
Avoids premature abstraction (constitution §IV — no premature complexity).

**Alternatives considered**:
- `AbstractParser` ABC with `CsvParser` subclass: rejected for v1 — only one implementation exists.
  Document as extension point for v2.

---

## Decision 6: Reuse save_to_json from Feature 001

**Decision**: `ExportResult` and `list[CsvRecord]` are passed to the existing
`factor_lib.serializers.json_serializer.save_to_json`. `CsvRecord` frozen dataclass
serializes via `default=str` (same as `ProjectDetailRecord`).

**Rationale**: DRY (constitution §IV — no copy-paste). `save_to_json` already handles
dataclasses, directory creation, and overwrite. Zero new code needed for US3.

**Alternatives considered**:
- Separate `export_save_to_json` function: rejected — identical logic; copy-paste anti-pattern.
