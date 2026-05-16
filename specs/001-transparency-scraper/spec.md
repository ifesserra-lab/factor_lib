# Feature Specification: Transparency Portal Scraper Library

**Feature Branch**: `001-transparency-scraper`
**Created**: 2026-05-16
**Status**: Draft
**Input**: User description: "criar uma lib em python usando playwright para buscar dados de projeto do portal de transparencia do https://facto.conveniar.com.br/portaltransparencia/. Ao clicar no botão consultar é listado todos os projetos. depois disso é necesário clicar na lupa .. para entrar em detalhes. A API deve varregar os detalhes da paginas e salvar tudo em um json"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List All Projects (Priority: P1)

A developer uses the library to retrieve a full list of projects from the transparency
portal. They call a single function that navigates to the portal, clicks the
"Consultar" button, and returns a structured list of all projects displayed on the
page.

**Why this priority**: Core entry point — without listing projects, no detail scraping
is possible. Delivers standalone value as a project directory.

**Independent Test**: Call `list_projects()` and assert the result is a non-empty list
of dicts, each containing at minimum a project identifier and a name field. Verifiable
against the live portal or a recorded HTML snapshot.

**Acceptance Scenarios**:

1. **Given** the portal is reachable, **When** `list_projects()` is called,
   **Then** returns a list with one or more project records, each as a dict.
2. **Given** the portal is reachable, **When** `list_projects()` is called,
   **Then** the "Consultar" button is clicked automatically with no manual interaction.
3. **Given** the portal returns zero results, **When** `list_projects()` is called,
   **Then** returns an empty list without raising an exception.

---

### User Story 2 - Scrape Project Details (Priority: P2)

A developer uses the library to retrieve full detail data for every project. The
library iterates the project list, clicks the magnifying-glass (lupa) icon for each
project, scrapes all visible fields from the detail page or modal, and aggregates the
results into a single JSON-serializable structure.

**Why this priority**: Highest-value data extraction step — transforms a list of
titles into rich, actionable project records.

**Independent Test**: Call `scrape_all_projects()` and assert each record in the
result contains more fields than the listing alone provides (e.g., budget, dates,
beneficiary, description). Verify no record is missing a detail entry.

**Acceptance Scenarios**:

1. **Given** a list of N projects, **When** `scrape_all_projects()` is called,
   **Then** returns exactly N detail records.
2. **Given** a project has a lupa icon, **When** the library processes that project,
   **Then** the icon is clicked and the detail view is fully loaded before data is read.
3. **Given** a detail page contains multiple labelled fields, **When** scraped,
   **Then** all visible labelled fields are captured as key-value pairs.
4. **Given** clicking the lupa fails for one project, **When** scraping continues,
   **Then** that project is recorded with an error marker and scraping proceeds to the
   next project without aborting.

---

### User Story 3 - Save Results to JSON (Priority: P3)

A developer uses the library to persist the complete scraped dataset to a JSON file.
They specify an output path; the library writes all project detail records as a JSON
array to that file.

**Why this priority**: Persistence makes the data reusable outside the library without
coupling callers to file I/O logic.

**Independent Test**: Call `save_to_json(records, path)` with a known record list and
assert the output file exists, is valid JSON, and contains the same number of records.

**Acceptance Scenarios**:

1. **Given** a list of project detail dicts, **When** `save_to_json(records, path)` is
   called, **Then** a file at `path` is created containing a valid JSON array.
2. **Given** an existing file at `path`, **When** `save_to_json` is called again,
   **Then** the file is overwritten with the new data.
3. **Given** the output directory does not exist, **When** `save_to_json` is called,
   **Then** the directory is created automatically before writing.

---

### Edge Cases

- What happens when the portal is unreachable (network error or timeout)?
- What happens when the page structure changes and the "Consultar" button cannot be found?
- What happens when a project's lupa icon is not interactive (disabled or hidden)?
- What happens when a detail page loads but contains no labelled fields?
- What happens when scraping a large number of projects causes memory or time pressure?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Library MUST navigate to the portal URL and click the "Consultar" button
  to trigger the full project listing without any additional filter input.
- **FR-002**: Library MUST extract all project records visible in the listing,
  including traversal of paginated results if pagination is present.
- **FR-003**: For each listed project, library MUST click the detail icon (lupa) and
  wait for the detail view to fully load before reading any data.
- **FR-004**: Library MUST capture all labelled fields from the detail view as
  key-value pairs, preserving original Portuguese field names as dict keys.
- **FR-005**: Library MUST add a scrape timestamp and source URL to each project
  detail record.
- **FR-006**: Library MUST serialize all collected project detail records into a
  JSON-compatible Python structure (list of dicts).
- **FR-007**: Library MUST provide a `save_to_json(records, path)` function that
  writes the collected data to a file, creating intermediate directories if needed.
- **FR-008**: Library MUST handle individual project scraping failures gracefully:
  log the error, mark the record with an error indicator, and continue to the next
  project without aborting the full run.
- **FR-009**: Library MUST expose a high-level function that performs the complete
  flow (list projects → scrape details → return results) with a single call.
- **FR-010**: Library MUST support headless browser execution suitable for
  server/CI environments with no display.

### Key Entities

- **Project Listing Record**: One row from the portal's project list; contains at
  minimum a unique project identifier and display name extracted from the listing page.
- **Project Detail Record**: All scraped fields from a project's detail view;
  key-value map of Portuguese field labels to their string values; includes
  `_source_url` and `_scraped_at` metadata fields; includes `_error` field when
  detail scraping failed.
- **Scrape Result**: Aggregate output — a list of Project Detail Records plus
  summary metadata (total scraped, total errors, run start timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A single function call completes the full portal scrape and produces a
  valid JSON-serializable result without manual browser interaction.
- **SC-002**: All projects visible in the portal listing are represented in the output
  (0% omission rate for reachable projects).
- **SC-003**: Each successfully scraped project detail record contains all labelled
  fields visible on the detail page (no silent field omission).
- **SC-004**: Scraping failure for one project does not prevent the remaining projects
  from being scraped and included in the output.
- **SC-005**: The library executes successfully in a headless, non-interactive
  environment (e.g., CI pipeline) without code modification.
- **SC-006**: Output JSON is valid and directly parseable by standard tooling without
  post-processing or manual cleanup.

## Assumptions

- The portal at `https://facto.conveniar.com.br/portaltransparencia/` is publicly
  accessible without authentication or CAPTCHA challenges.
- The "Consultar" button triggers the full project listing without requiring any
  additional filter input to be filled.
- The magnifying-glass (lupa) element opens a detail view within the same page or in
  a modal — not in a new browser tab.
- All detail fields are rendered as visible HTML text; no OCR or image parsing is
  required.
- Sequential (one-at-a-time) project scraping is sufficient for v1; parallel scraping
  is out of scope.
- Output format is a flat JSON array of objects; nested or relational structures are
  out of scope.
- The library is designed for programmatic use by developers; a CLI wrapper is out of
  scope for v1.
