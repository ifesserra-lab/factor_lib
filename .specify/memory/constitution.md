<!--
  Sync Impact Report
  Version change: 1.0.0 → 1.1.0 (MINOR)
  Modified principles:
    §I Test-First Development — expanded: added pytest as mandatory runner,
       test pyramid (unit > integration > E2E), commit-order enforcement,
       explicit Red/Green/Refactor commit discipline
    §III OO + Design Patterns — expanded: added project-specific pattern list
       (POM, Strategy, Facade, Factory, Value Object) with mandatory application rules
  Added sections: none
  Removed sections: none
  Templates requiring updates:
    ✅ plan-template.md — Constitution Check gates updated to reflect §I and §III expansions
    ✅ tasks-template.md — test-first task ordering already enforced; pytest runner matches §I
    ✅ spec-template.md — no change required
  Follow-up TODOs: none
-->

# factor_lib Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory. No production code may exist without a preceding failing test.
The Red-Green-Refactor cycle MUST be strictly followed for every unit of behavior:

1. **Red** — Write a test that fails. Commit it. The CI run MUST be red.
2. **Green** — Write the minimum code to make the test pass. Commit it separately.
3. **Refactor** — Improve structure while keeping tests green. Commit separately.

**Commit order is law**: the failing-test commit MUST precede the implementation
commit in git history. Reviewers MUST verify this order via `git log` before approval.
Tests written after implementation do NOT satisfy this principle and MUST be rejected.

**pytest is the mandatory test runner** for all unit and integration tests.
`pytest-playwright` is the mandatory runner for E2E tests. No other test framework
may be used without explicit project-lead approval.

**Test pyramid** — three levels, all mandatory:

| Level | Location | Scope | Speed |
|-------|----------|-------|-------|
| Unit | `tests/unit/` | Single class/function; no I/O | < 1s each |
| Integration | `tests/integration/` | Real filesystem; no browser | < 5s each |
| E2E | `tests/e2e/` | Full browser flow via Playwright | < 30s each |

Each level MUST have tests before the corresponding implementation is merged.
Coverage gates apply at all three levels; a green unit suite does not excuse a
missing integration or E2E test for the same behavior.

**Rationale**: TDD prevents regressions, forces modular design, and makes behavior
explicit before implementation — reducing debugging cost and design drift. Commit
order verification provides auditable proof of TDD compliance.

### II. Python as Primary Language

All production code MUST be written in Python 3.11+. Idiomatic Python MUST be used:
PEP 8 style, type hints on all public interfaces, dataclasses for value objects,
context managers for resource management. Dependencies MUST be managed via
`pyproject.toml` with pinned versions. External scripts in other languages require
explicit project-lead approval.

**Rationale**: A single-language codebase reduces cognitive overhead and tooling
complexity. Python's ecosystem supports the project's testing and automation goals.

### III. Object-Oriented Design with Design Patterns

Code MUST be organized using OO principles. Design patterns MUST be applied when they
reduce complexity. Pattern choice MUST be documented inline when non-obvious to a
reviewer. Choosing no pattern where one is clearly applicable is a violation.

**SOLID principles are non-negotiable**:

- **S** — Single Responsibility: each class has one reason to change.
- **O** — Open/Closed: extend behavior without modifying existing code.
- **L** — Liskov Substitution: subtypes must be substitutable for their base types.
- **I** — Interface Segregation: prefer small, focused abstractions.
- **D** — Dependency Inversion: depend on abstractions, not concretions.

**Required patterns for this project** (apply wherever the problem fits):

| Pattern | When to apply |
|---------|--------------|
| **Page Object Model (POM)** | Every Playwright page interaction; locators live only in page objects |
| **Strategy** | Interchangeable algorithms (scrapers, parsers, exporters) |
| **Facade** | High-level public API functions that compose subsystems |
| **Factory** | Centralised creation of browser, page, or configured objects |
| **Value Object / Dataclass** | Immutable domain records (frozen dataclasses) |

Using a pattern NOT in this table requires a comment explaining the choice.
Skipping a pattern from this table where it clearly applies requires justification in
the plan's Complexity Tracking section.

**Rationale**: OO with patterns yields readable, maintainable, extensible code.
Named patterns create a shared vocabulary that accelerates code review and onboarding.

### IV. Zero Tolerance for Anti-Patterns

The following anti-patterns are FORBIDDEN and MUST be caught in code review:

- **God Object / Blob class** — class with too many responsibilities.
- **Spaghetti code** — unstructured flow, deeply nested conditionals.
- **Copy-paste programming** — DRY violations; extract shared logic.
- **Magic numbers / magic strings** — use named constants or enums.
- **Premature optimization** — optimize only after profiling proves necessity.
- **Yo-Yo problem** — excessive, unjustified inheritance chains.
- **Anemic Domain Model** — data classes with no behavior; logic scattered elsewhere.
- **Singleton abuse** — use dependency injection instead of global state.

PRs introducing any of the above MUST be rejected. Existing violations discovered
during review MUST be refactored in a dedicated commit before merge.

**Rationale**: Anti-patterns accumulate technical debt exponentially. Zero tolerance
keeps the codebase sustainable long-term.

### V. End-to-End Testing with Playwright

All UI and workflow E2E tests MUST use Playwright (Python `playwright` package).
E2E tests MUST be written before UI implementation (TDD §I applies to E2E too).
Tests MUST run in CI and MUST NOT depend on live external services — use Playwright's
`page.route()` network interception for mocking. The Page Object Model (POM) pattern
MUST be used for all Playwright test suites (see §III).

**Rationale**: Playwright provides reliable, cross-browser E2E coverage. POM prevents
test fragility and keeps tests maintainable as the UI evolves.

## Development Workflow

- All features MUST start from a failing test — no exceptions.
- Feature branches MUST follow `###-feature-name` naming convention.
- Each commit MUST leave the test suite green; broken-test commits are not allowed.
- Exception: the deliberate Red commit in TDD §I step 1 is the only allowed red commit,
  and it MUST be immediately followed by the Green commit.
- Refactoring MUST happen in its own commit, separate from feature commits.
- Code reviews MUST verify: test-commit order (§I), pattern compliance (§III),
  zero anti-patterns (§IV), test pyramid coverage (§I).
- New dependencies require justification; no transitive dependency pinning without
  explicit approval.

## Quality Gates

Every PR MUST pass all of the following before merge:

1. **Tests green** — unit, integration, and E2E (Playwright) suites all pass.
2. **TDD evidence** — failing-test commit precedes implementation commit in `git log`.
3. **Test pyramid complete** — all three levels have tests for new behavior.
4. **No anti-patterns** — reviewer confirms none from the §IV forbidden list.
5. **OO + SOLID + Patterns** — required patterns applied; SOLID violations absent.
6. **Type hints complete** — `mypy --strict` passes with zero errors.
7. **Linting** — `ruff check` passes with zero warnings.

## Governance

This constitution supersedes all other coding practices and style guides on this
project. Amendments require:

1. Written proposal with rationale and impact assessment.
2. Approval by project lead.
3. Migration plan for code currently violating the new or changed rule.
4. Version bump following the policy below.

**Versioning Policy**:
- MAJOR: Removal or redefinition of an existing principle.
- MINOR: New principle or materially expanded guidance added.
- PATCH: Clarifications, wording fixes, non-semantic refinements.

All PRs and reviews MUST verify compliance with this constitution. Complexity
violations MUST be justified in the plan's Complexity Tracking table.

**Version**: 1.1.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
