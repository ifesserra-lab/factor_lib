"""JSON serialization utility. Reused by both feature 001 and feature 002."""
import dataclasses
import json
import os
from pathlib import Path
from typing import Any


def _to_serializable(record: Any) -> Any:
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return record.to_dict()
    if dataclasses.is_dataclass(record) and not isinstance(record, type):
        return dataclasses.asdict(record)
    return record


def save_to_json(
    records: "list[Any] | Any",
    path: "str | os.PathLike[str]",
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Serialize a list of records (or ScrapeResult) to a JSON file."""
    # Accept ScrapeResult by extracting its records tuple
    if hasattr(records, "records") and not isinstance(records, list):
        records = list(records.records)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = [_to_serializable(r) for r in records]
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(serialized, fh, indent=indent, ensure_ascii=ensure_ascii, default=str)
