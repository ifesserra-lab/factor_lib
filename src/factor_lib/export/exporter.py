"""Facade: single-call CSV export flow (download → parse → save)."""
from __future__ import annotations

import os
from datetime import datetime

from factor_lib.export.csv_parser import parse_zip_csv
from factor_lib.export.downloader import download_csv_export
from factor_lib.export.exceptions import ExportError
from factor_lib.export.models import ExportResult
from factor_lib.serializers import save_to_json


def export_project_csv_to_json(
    page: object,
    output_path: str | os.PathLike[str],
    *,
    timeout: int = 60_000,
    indent: int = 2,
) -> ExportResult:
    """Download CSV ZIP, parse all CSVs, write JSON file.

    Caller must already be on the project detail page.
    Each stage is wrapped; failure re-raised as ExportError with stage label.
    """
    exported_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        zip_bytes = download_csv_export(page, timeout=timeout)  # type: ignore[arg-type]
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(stage="download", reason=str(exc)) from exc

    try:
        records = parse_zip_csv(zip_bytes)
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(stage="parse", reason=str(exc)) from exc

    try:
        save_to_json(list(records), output_path, indent=indent)
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(stage="save", reason=str(exc)) from exc

    files = len({r.source_file for r in records})
    return ExportResult(
        records=tuple(records),
        total_records=len(records),
        files_processed=files,
        errors=(),
        exported_at=exported_at,
    )
