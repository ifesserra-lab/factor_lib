# Feature Specification: CSV Export to JSON Processor

**Feature Branch**: `002-csv-export-to-json`
**Created**: 2026-05-16
**Status**: Draft
**Input**: User description: "na pagina de detalhes clique em exportar em csv. baixar o arquivo zip abrir e processar e salvar tudo em json"

## Clarifications

### Session 2026-05-16

- Q: Who controls the ZIP file lifecycle — library-managed temp dir with auto-delete, or caller-owned path? → A: Library manages temp dir and auto-deletes ZIP after parsing (Option A)
- Q: Maximum wait time for ZIP download before raising an error? → A: 60 seconds
- Q: How should empty rows in CSV be handled? → A: Skip silently; log count at debug level
- Q: If export button triggers redirect instead of direct download, what should library do? → A: Follow redirect and attempt download from final destination URL
- Q: Should CSV export be packaged inside `factor_lib` or as a separate library? → A: Same `factor_lib` package — `from factor_lib.export import export_project_csv_to_json`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trigger CSV Export Download (Priority: P1)

A developer uses the library while on a project detail page. The library locates and
clicks the "Exportar em CSV" button, waits for the download to complete, and returns
the path to the downloaded ZIP file.

**Why this priority**: Without successfully downloading the ZIP, no processing is
possible. This is the entry point for the entire export flow.

**Independent Test**: Call `download_csv_export(page)` while on a detail page and
assert that a ZIP file is present at the returned path and is non-zero in size.

**Acceptance Scenarios**:

1. **Given** the detail page is loaded and the "Exportar em CSV" button is visible,
   **When** `download_csv_export(page)` is called, **Then** the button is clicked
   and a ZIP file is downloaded to a known local path.
2. **Given** the download is triggered, **When** the download completes,
   **Then** the returned path points to a file that exists and has size > 0.
3. **Given** the "Exportar em CSV" button is not present on the page,
   **When** `download_csv_export(page)` is called, **Then** an informative error
   is raised without crashing the process.

---

### User Story 2 - Extract and Parse CSV from ZIP (Priority: P2)

A developer passes the downloaded ZIP file path to the library. The library opens the
ZIP, locates the CSV file(s) inside, parses each CSV, and returns all rows as a list
of dicts with column headers as keys.

**Why this priority**: Transforms the raw downloaded archive into structured data —
the core data-processing step that enables JSON output.

**Independent Test**: Call `parse_zip_csv(zip_path)` with a pre-downloaded ZIP
fixture and assert the result is a non-empty list of dicts whose keys match the CSV
header columns.

**Acceptance Scenarios**:

1. **Given** a valid ZIP file containing one or more CSV files, **When**
   `parse_zip_csv(zip_path)` is called, **Then** returns a list of dicts, one per
   CSV row, with column headers as keys.
2. **Given** a ZIP containing multiple CSV files, **When** parsed, **Then** rows from
   all CSV files are merged into a single list, each record tagged with its source
   filename.
3. **Given** a ZIP with no CSV files, **When** `parse_zip_csv` is called, **Then**
   returns an empty list and logs a warning.
4. **Given** a CSV with non-UTF-8 encoding, **When** parsed, **Then** the library
   attempts common Brazilian Portuguese encodings (Latin-1 / ISO-8859-1) as fallback
   before raising an error.

---

### User Story 3 - Save Parsed Records to JSON (Priority: P3)

A developer provides the list of parsed CSV records and an output file path. The
library serializes the records to a JSON file at that path, creating any missing
parent directories.

**Why this priority**: Persists the structured data for downstream consumption;
mirrors the save behavior from the scraper feature (spec 001).

**Independent Test**: Call `save_to_json(records, path)` with known records and
assert the output file is valid JSON containing the same number of records with
identical content.

**Acceptance Scenarios**:

1. **Given** a list of CSV-derived dicts, **When** `save_to_json(records, path)` is
   called, **Then** a file at `path` is created containing a valid JSON array.
2. **Given** a file already exists at `path`, **When** `save_to_json` is called,
   **Then** the file is overwritten with the new data.
3. **Given** parent directories of `path` do not exist, **When** `save_to_json` is
   called, **Then** directories are created before writing the file.

---

### User Story 4 - End-to-End Export Flow (Priority: P4)

A developer calls a single high-level function that, given an already-open detail
page, performs the full export flow: clicks the export button, downloads the ZIP,
parses the CSV(s), and returns the structured records — optionally saving to a JSON
file in one step.

**Why this priority**: Convenience wrapper that composes P1–P3 stories into a single
callable, reducing integration code for callers.

**Independent Test**: Call `export_project_csv_to_json(page, output_path)` and assert
the output JSON file is created and contains the expected records from that project.

**Acceptance Scenarios**:

1. **Given** a detail page is open, **When**
   `export_project_csv_to_json(page, output_path)` is called, **Then** a JSON file
   is written at `output_path` containing all CSV rows as structured records.
2. **Given** the export fails at any stage, **When** the high-level function is called,
   **Then** the error is surfaced with a clear message indicating which stage failed.

---

### Edge Cases

- What happens when the ZIP is corrupted or not a valid ZIP archive?
- Empty rows in CSV are silently skipped; the count of skipped rows is logged at debug level. Rows with mismatched column counts are treated as partial records: missing columns default to empty string.
- What happens when the download takes longer than expected (slow portal response)?
- If the "Exportar em CSV" button triggers a redirect, the library MUST follow the redirect chain and attempt to download from the final destination URL. If no downloadable file is found at the final URL, `ExportError` is raised.
- What happens when CSV numeric fields use Brazilian decimal notation (comma as
  decimal separator)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Library MUST locate and click the "Exportar em CSV" button on the detail
  page to initiate the file download. If the button triggers a redirect, the library
  MUST follow the redirect chain and attempt to download from the final URL.
- **FR-002**: Library MUST download the ZIP to a library-managed temporary directory,
  parse it, and delete the temporary files automatically after parsing completes
  (regardless of success or failure). The caller MUST NOT need to manage temp files.
- **FR-003**: Library MUST open the downloaded ZIP archive and enumerate all CSV files
  within it.
- **FR-004**: Library MUST parse each CSV file into a list of dicts using column
  headers as keys. Empty rows MUST be skipped silently with a debug-level log of the
  total count skipped. Rows with fewer columns than headers MUST default missing
  values to empty string.
- **FR-005**: Library MUST tag each parsed record with its source CSV filename when
  multiple CSV files are present in the ZIP.
- **FR-006**: Library MUST attempt Brazilian Portuguese character encoding fallbacks
  (Latin-1 / ISO-8859-1) when a CSV is not valid UTF-8.
- **FR-007**: Library MUST serialize parsed records to a JSON file at a caller-
  specified path, creating intermediate directories as needed.
- **FR-008**: Library MUST expose a high-level function composing the full export flow
  (click → download → parse → save) in a single call.
- **FR-009**: Library MUST handle errors at each stage (missing button, corrupt ZIP,
  unparseable CSV) with informative exceptions and without silent data loss.
- **FR-011**: Library MUST raise a timeout error if the ZIP download does not complete
  within 60 seconds. The timeout MUST be configurable by the caller.
- **FR-010**: Library MUST add metadata to each record: source CSV filename, ZIP file
  path, and extraction timestamp.

### Key Entities

- **Export ZIP**: The archive file downloaded from the portal's "Exportar em CSV"
  action; contains one or more CSV files representing project data.
- **CSV Record**: One row from a parsed CSV file; represented as a dict mapping
  column header strings to string values; includes `_source_file` and `_extracted_at`
  metadata fields.
- **Export Result**: The complete output — a list of CSV Records plus summary metadata
  (total records, total files processed, errors if any, export timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single function call on an open detail page produces a valid JSON file
  containing all rows from all CSV files in the downloaded ZIP.
- **SC-002**: Every row present in the source CSV(s) appears in the output JSON with
  no omissions (100% row coverage for parseable files).
- **SC-003**: All column values are preserved exactly as they appear in the CSV,
  including Portuguese characters and formatting.
- **SC-004**: Errors at any stage (download, extract, parse, save) produce a clear,
  actionable error message and do not result in a silently incomplete output file.
- **SC-005**: The feature operates correctly in a headless, non-interactive environment
  without manual intervention.

## Assumptions

- The "Exportar em CSV" button triggers a direct file download (ZIP format); the
  portal does not require additional confirmation dialogs before downloading.
- The ZIP archive contains at least one CSV file; binary or non-CSV files inside the
  ZIP are ignored without error.
- CSV files inside the ZIP use Portuguese field names as column headers.
- Numeric fields may use Brazilian decimal notation (comma as decimal separator);
  values are preserved as strings in JSON to avoid locale-dependent parsing errors.
- The library creates a temporary directory for the downloaded ZIP, parses it, then
  deletes the ZIP and temp directory automatically. The caller is never responsible
  for ZIP file cleanup.
- This feature is packaged inside the same `factor_lib` package as spec 001,
  under the `factor_lib.export` module. Callers import via
  `from factor_lib.export import export_project_csv_to_json`. Shared utilities
  (browser lifecycle, `save_to_json`) are reused from `factor_lib` core.
- The caller is responsible for navigating to the correct detail page before
  invoking the export functions.
- Parallel processing of multiple projects' CSV exports is out of scope for v1.
