#!/usr/bin/env bash
# Scans specs/ and reports feature status for docs update.
# Called by speckit.docs.update hook; actual doc rewrite is done by the AI skill.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SPECS_DIR="$REPO_ROOT/specs"
DOCS_DIR="$REPO_ROOT/docs"
TODAY="$(date +%Y-%m-%d)"

if [ ! -d "$SPECS_DIR" ]; then
  echo "[docs] No specs/ directory found — skipping docs update."
  exit 0
fi

echo "[docs] Scanning specs/ for feature status..."

feature_count=0
us_count=0

for spec_dir in "$SPECS_DIR"/*/; do
  [ -d "$spec_dir" ] || continue
  feature_name="$(basename "$spec_dir")"
  has_spec="false"; has_plan="false"; has_tasks="false"

  [ -f "$spec_dir/spec.md" ]  && has_spec="true"
  [ -f "$spec_dir/plan.md" ]  && has_plan="true"
  [ -f "$spec_dir/tasks.md" ] && has_tasks="true"

  if [ "$has_spec" = "true" ]; then
    feature_count=$((feature_count + 1))
    count=$(grep -c "^### User Story" "$spec_dir/spec.md" 2>/dev/null || echo 0)
    us_count=$((us_count + count))
    echo "[docs]   $feature_name — spec=$has_spec plan=$has_plan tasks=$has_tasks us=$count"
  fi
done

echo "[docs] Found $feature_count features, $us_count user stories."
echo "[docs] Docs dir: $DOCS_DIR"
echo "[docs] Today: $TODAY"
echo "[docs] STATUS_JSON={\"features\":$feature_count,\"user_stories\":$us_count,\"date\":\"$TODAY\",\"specs_dir\":\"$SPECS_DIR\",\"docs_dir\":\"$DOCS_DIR\"}"
