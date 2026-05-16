Base directory for this skill: /Users/paulossjunior/projects/diretoria/factor_lib/.claude/skills/speckit-docs-update

# Update Project Documentation

Regenerate `docs/` from current spec artifacts after any Spec Kit command completes.
Triggered automatically via `speckit.docs.update` hooks in `.specify/extensions.yml`.

## Execution

1. Run `.specify/scripts/bash/update-docs.sh` and parse `STATUS_JSON` line.
2. For each feature directory found in `specs/`:
   - Read `spec.md` — extract epic title, branch, all User Stories (title + priority)
   - Read `plan.md` if exists — extract Technical Context and architectural decisions table
   - Read `tasks.md` if exists — note tasks generated status
3. Derive status per feature:
   - spec.md exists → "Especificado ✅"
   - plan.md exists → "Planejado ✅"
   - tasks.md exists → "Tasks geradas ✅"
   - src/ implementation files exist → "Em andamento 🔄"
4. Rewrite `docs/backlog.md`:
   - Update **Last Updated** date at top
   - Sync épicos table (one row per feature)
   - Sync US tables (one row per User Story per epic)
5. Rewrite `docs/epics-and-user-stories.md`:
   - Update **Last Updated** date at top
   - Add/update sections for new epics and user stories
   - Preserve manually written sections not derived from specs
6. Update `docs/architecture.md`:
   - Update **Last Updated** date at top
   - Sync architectural decisions table from all plan.md files
   - Preserve manually written sections (principles table, patterns, etc.)
7. Print: `docs/ updated: N features, M user stories synced.`

## Rules

- NEVER delete manually written sections that have no spec equivalent.
- ALWAYS preserve the architecture principles table (manually maintained in architecture.md).
- ALWAYS update "Last Updated" at top of each doc.
- Keep Given/When/Then format for acceptance scenarios.
- Dependency map at bottom of epics-and-user-stories.md is auto-generated from spec priorities.
- If a feature is removed from specs/, mark it as Cancelado ❌ in backlog (never delete the row).

## Output

`docs/ updated: N features, M user stories synced. Files: backlog.md, epics-and-user-stories.md, architecture.md`
