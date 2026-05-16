<!--
  Sync Impact Report
  Version change: — → 1.0.0 (initial ratification)
  Added sections: Core Principles (I–V), Development Workflow, Quality Gates, Governance
  Removed sections: N/A (first version)
  Templates requiring updates:
    ✅ plan-template.md — Constitution Check section references constitution; TDD/Python/Playwright gates apply
    ✅ spec-template.md — acceptance criteria align with TDD principle; Playwright E2E scenarios expected
    ✅ tasks-template.md — test-first task ordering (write test → fail → implement) already enforced
  Follow-up TODOs: None — all placeholders resolved
-->

# factor_lib Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory. Every piece of production code MUST be preceded by a failing test.
The Red-Green-Refactor cycle MUST be strictly followed:

1. Write a test that fails (Red).
2. Write the minimum code to make it pass (Green).
3. Refactor while keeping tests green (Refactor).

No production code may be merged without a corresponding test. Coverage gates apply at
all levels: unit, integration, and end-to-end. Tests written after implementation do
not satisfy this principle.

**Rationale**: TDD prevents regressions, forces modular design, and makes behavior
explicit before implementation—reducing debugging cost and design drift.

### II. Python as Primary Language

All production code MUST be written in Python. Idiomatic Python MUST be used:
PEP 8 style, type hints on all public interfaces, dataclasses for value objects,
context managers for resource management. Dependencies MUST be managed via
`pyproject.toml` with pinned versions. External scripts in other languages require
explicit project-lead approval.

**Rationale**: A single-language codebase reduces cognitive overhead and tooling
complexity. Python's ecosystem supports the project's testing and automation goals.

### III. Object-Oriented Design with Design Patterns

Code MUST be organized using OO principles. Recognized GoF and enterprise patterns
MUST be applied when they reduce complexity; pattern choice MUST be documented inline
when non-obvious to a reviewer.

SOLID principles are non-negotiable:

- **S** — Single Responsibility: each class has one reason to change.
- **O** — Open/Closed: extend behavior without modifying existing code.
- **L** — Liskov Substitution: subtypes must be substitutable for their base types.
- **I** — Interface Segregation: prefer small, focused abstractions.
- **D** — Dependency Inversion: depend on abstractions, not concretions.

**Rationale**: OO with patterns yields readable, maintainable, extensible code without
ad-hoc workarounds accumulating into technical debt.

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
E2E tests MUST be written before UI implementation (TDD applies to E2E too).
Tests MUST run in CI and MUST NOT depend on live external services — use Playwright's
network interception for mocking. The Page Object Model (POM) pattern MUST be used
for all Playwright test suites.

**Rationale**: Playwright provides reliable, cross-browser E2E coverage. POM prevents
test fragility and keeps tests maintainable as the UI evolves.

## Development Workflow

- All features MUST start from a failing test — no exceptions.
- Feature branches MUST follow `###-feature-name` naming convention.
- Each commit MUST leave the test suite green; broken-test commits are not allowed.
- Refactoring MUST happen in its own commit, separate from feature commits.
- Code reviews MUST verify: test coverage, pattern compliance, zero anti-patterns.
- New dependencies require justification; no transitive dependency pinning without
  explicit approval.

## Quality Gates

Every PR MUST pass all of the following before merge:

1. **Tests green** — unit, integration, and E2E (Playwright) suites all pass.
2. **No anti-patterns** — reviewer confirms none from the §IV forbidden list.
3. **OO + SOLID compliance** — design pattern use is evident and appropriate.
4. **Type hints complete** — `mypy --strict` (or equivalent) passes with zero errors.
5. **Linting** — `ruff` or `flake8` passes with zero warnings.
6. **TDD evidence** — failing-test commit precedes implementation commit in history.

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

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
