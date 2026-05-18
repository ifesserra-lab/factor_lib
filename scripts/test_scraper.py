#!/usr/bin/env python3
"""Smoke test + full scrape for factor_lib — runs against live portal."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Allow running from repo root without installing package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import factor_lib as fl

# ---------------------------------------------------------------------------
# Logging: console + file (data/run_TIMESTAMP.log)
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = OUTPUT_DIR / f"run_{TIMESTAMP}.log"

_fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")

_file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_fmt)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))

logging.root.setLevel(logging.DEBUG)
logging.root.addHandler(_file_handler)
logging.root.addHandler(_console_handler)

log = logging.getLogger("test_scraper")


def step(msg: str) -> None:
    line = "=" * 60
    log.info("%s", line)
    log.info("  %s", msg)
    log.info("%s", line)


def ok(msg: str) -> None:
    log.info("[OK]  %s", msg)


def fail(msg: str) -> None:
    log.error("[FAIL] %s", msg)


log.info("Log file: %s", LOG_PATH)

# ---------------------------------------------------------------------------
# Step 1: list_projects — verify portal reachable
# ---------------------------------------------------------------------------
step("STEP 1 — list_projects()")
try:
    projects = fl.list_projects()
    assert isinstance(projects, list) and len(projects) > 0
    ok(f"Found {len(projects)} projects")
    ok(f"First: id={projects[0].id!r} name={projects[0].name[:60]!r}")
except fl.PortalNavigationError as exc:
    fail(f"PortalNavigationError: {exc}")
    log.debug("Exception detail", exc_info=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 2: scrape_all_projects — all projects, full detail
# ---------------------------------------------------------------------------
WORKERS = 4

step(f"STEP 2 — scrape_all_projects() [{len(projects)} projects, {WORKERS} workers]")
log.info("  estimated: ~%d min", max(1, len(projects) * 15 // WORKERS // 60))
try:
    result = fl.scrape_all_projects(workers=WORKERS)
    assert isinstance(result, fl.ScrapeResult)
    assert result.success_count + result.error_count == result.total
    ok(f"ScrapeResult: total={result.total} success={result.success_count} errors={result.error_count}")
    for rec in result.records:
        status = "ERR" if rec._error else "OK "
        fields_info = f"{len(rec.fields)} fields" if not rec._error else rec._error[:80]
        log.info("  [%s] %s — %s", status, rec.id.rjust(4), fields_info)
except fl.PortalNavigationError as exc:
    fail(f"PortalNavigationError: {exc}")
    log.debug("Exception detail", exc_info=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 3: save one JSON file per project
# ---------------------------------------------------------------------------
step("STEP 3 — save one file per project")
projects_dir = OUTPUT_DIR / f"projects_{TIMESTAMP}"
projects_dir.mkdir(parents=True, exist_ok=True)
try:
    saved = 0
    for rec in result.records:
        # Fields contain JSON-stringified CSV sections (key=csv_filename, value=json rows)
        csv_sections: dict = {}
        for section_name, rows_json in rec.fields.items():
            try:
                csv_sections[section_name] = json.loads(rows_json)
            except (json.JSONDecodeError, TypeError):
                csv_sections[section_name] = rows_json

        doc = {
            "id": rec.id,
            "name": rec.name,
            "csv": csv_sections,
            "_source_url": rec._source_url,
            "_scraped_at": rec._scraped_at,
            "_error": rec._error,
        }
        out = projects_dir / f"project_{rec.id}.json"
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        saved += 1
        log.debug("  saved %s", out.name)
    assert saved == result.total
    ok(f"Saved {saved} files → {projects_dir}/")
    sample = json.loads((projects_dir / f"project_{result.records[0].id}.json").read_text())
    ok(f"Top-level keys: {list(sample.keys())}")
    ok(f"CSV sections: {list(sample.get('csv', {}).keys())[:4]}")
except (AssertionError, OSError) as exc:
    fail(str(exc))
    log.debug("Exception detail", exc_info=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 4: save errors report JSON
# ---------------------------------------------------------------------------
step("STEP 4 — save errors report")
errors_report_path = projects_dir / "errors_report.json"
try:
    failed_records = [rec for rec in result.records if rec._error]
    errors_doc = {
        "generated_at": TIMESTAMP,
        "total": result.total,
        "success_count": result.success_count,
        "error_count": result.error_count,
        "errors": [
            {
                "id": rec.id,
                "name": rec.name,
                "error": rec._error,
                "source_url": rec._source_url,
            }
            for rec in failed_records
        ],
    }
    errors_report_path.write_text(
        json.dumps(errors_doc, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ok(f"Saved errors report → {errors_report_path.name} ({len(failed_records)} entries)")
except OSError as exc:
    fail(str(exc))
    log.debug("Exception detail", exc_info=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
step("ALL STEPS PASSED")
log.info("  Output dir  : %s", projects_dir)
log.info("  Log file    : %s", LOG_PATH)
log.info("  Total: %d | OK: %d | Errors: %d", result.total, result.success_count, result.error_count)
log.info("  Files: %d × project_<id>.json", result.total)
