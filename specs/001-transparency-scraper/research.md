# Research: Transparency Portal Scraper Library

**Feature**: 001-transparency-scraper
**Date**: 2026-05-16

---

## Decision 1: Playwright Sync vs Async API

**Decision**: Use Playwright **sync API** (`playwright.sync_api`).

**Rationale**: Library is consumed by developers in simple scripts and CI pipelines.
Sync API eliminates `async/await` boilerplate for callers. Async offers no throughput
benefit given sequential scraping requirement. `pytest-playwright` fixtures use sync
API by default, reducing test complexity.

**Alternatives considered**:
- Async API (`playwright.async_api`): rejected — adds caller overhead with no v1
  benefit; can be offered as v2 extension without breaking existing sync interface.

---

## Decision 2: Page Object Model Structure

**Decision**: Two-level POM: `BasePage` (shared wait helpers) → `TransparencyPortalPage`
(portal-specific interactions: click Consultar, iterate rows, click lupa, read detail
fields).

**Rationale**: POM mandated by constitution §V. Single portal page encapsulates all
locator knowledge in one class; changing selectors only touches one file (OCP). Split
into listing + detail methods on the same class avoids over-engineering for a single-
portal library.

**Alternatives considered**:
- Separate `ListingPage` and `DetailPage` classes: rejected for v1 — the portal
  appears to show details inline/modal on the same URL, so one page object is simpler.
  Can be refactored to two classes when portal navigation changes (OCP satisfied).

---

## Decision 3: Scraper Strategy Pattern

**Decision**: `AbstractScraper` protocol / ABC with `ListingScraper` and
`DetailScraper` as concrete strategies. `PortalScraper` (facade) composes both.

**Rationale**: Strategy pattern (GoF) makes each scraping concern independently
testable and replaceable. `DetailScraper` can be swapped without touching listing
logic. Satisfies OCP and SRP from constitution §III.

**Alternatives considered**:
- Monolithic scraper function: rejected — violates SRP; untestable in isolation.
- Separate independent classes with no shared interface: rejected — violates DIP;
  hard to mock in tests.

---

## Decision 4: Packaging and Dependency Management

**Decision**: `pyproject.toml` with `[project]` metadata; `src/` layout; Playwright
browsers installed via `playwright install chromium`.

**Rationale**: `src/` layout prevents accidental imports of uninstalled package.
`pyproject.toml` is the modern Python standard (PEP 517/518). Pinning Playwright
version in `[project.dependencies]` ensures reproducible CI runs. Constitution §II
mandates `pyproject.toml`.

**Alternatives considered**:
- `setup.py` / `requirements.txt`: rejected — legacy; no build-system isolation.

---

## Decision 5: Wait Strategy for Dynamic Content

**Decision**: Use Playwright's `page.wait_for_selector()` and `page.wait_for_load_state("networkidle")`
after each navigation action. Configurable timeout via constructor parameter (default
30 seconds).

**Rationale**: The portal is a Brazilian government web application likely built on
a server-rendered or partial-SPA framework. `networkidle` is the safest default for
pages with AJAX content that may not emit `DOMContentLoaded` reliably. Configurable
timeout supports slow connections and CI throttling.

**Alternatives considered**:
- Fixed `sleep()` delays: rejected — brittle, slow, non-deterministic.
- `wait_for_load_state("load")`: rejected — insufficient for AJAX-rendered content.

---

## Decision 6: Test Isolation for E2E Tests

**Decision**: Use Playwright's `page.route()` network interception to mock portal
responses from recorded HTML snapshots. Store snapshots as fixtures in
`tests/e2e/fixtures/`.

**Rationale**: Constitution §V forbids E2E tests depending on live external services.
Recording snapshots at development time and replaying them in CI ensures deterministic
tests regardless of portal availability. POM + route mocking = fast, reliable E2E.

**Alternatives considered**:
- Live portal in CI: rejected — violates constitution §V; fragile to portal changes.
- Full Playwright `--record` mode only: complements but does not replace route mocking.

---

## Decision 7: Data Serialization

**Decision**: Python `dataclasses` for models; `json.dumps` with `default=str` for
serialization; no third-party serialization library.

**Rationale**: `dataclasses` are idiomatic Python (constitution §II); lightweight;
no extra dependency. `default=str` handles datetime serialization gracefully.
`dataclasses-json` adds complexity without benefit for this simple flat structure.

**Alternatives considered**:
- `pydantic`: rejected — heavy dependency; overly complex for flat key-value records.
- `dataclasses-json`: removed from dependencies — `json.dumps` sufficient.
