"""Value objects for factor_lib.export: CsvRecord and ExportResult."""
from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class CsvRecord:
    """One row from a CSV file inside the downloaded ZIP (Value Object)."""

    fields: dict[str, str]
    source_file: str
    extracted_at: str  # ISO 8601

    def to_dict(self) -> dict[str, Any]:
        """Return a flat dict with CSV fields merged at root level."""
        return {
            **self.fields,
            "_source_file": self.source_file,
            "_extracted_at": self.extracted_at,
        }


@dataclasses.dataclass(frozen=True)
class ExportResult:
    """Aggregate output of a full export run (Value Object)."""

    records: tuple[CsvRecord, ...]
    total_records: int
    files_processed: int
    errors: tuple[str, ...]
    exported_at: str  # ISO 8601
