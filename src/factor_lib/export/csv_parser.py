"""Parse all CSVs from a ZIP archive into a flat list of CsvRecord."""
from __future__ import annotations

import csv
import io
import logging
import zipfile
from datetime import datetime

from factor_lib.export.exceptions import ParseError
from factor_lib.export.models import CsvRecord

_LOG = logging.getLogger(__name__)


def parse_zip_csv(zip_bytes: bytes) -> list[CsvRecord]:
    """Open a ZIP from bytes, parse every .csv member, return flat list of CsvRecord.

    Encoding: tries UTF-8 first, falls back to Latin-1/ISO-8859-1.
    Empty rows are silently skipped (count logged at DEBUG level).
    Rows shorter than the header default missing columns to "".
    Returns [] if ZIP contains no CSV files.
    Raises ParseError if ZIP is corrupt or a CSV cannot be decoded.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        raise ParseError(stage="parse", reason=f"ZIP archive is corrupt: {exc}") from exc

    records: list[CsvRecord] = []
    extracted_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    with zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            _LOG.warning("ZIP contains no CSV files — returning empty list")
            return []

        for csv_name in csv_names:
            raw_bytes = zf.read(csv_name)
            text = _decode(csv_name, raw_bytes)
            file_records = _parse_csv(text, csv_name, extracted_at)
            records.extend(file_records)

    return records


def _decode(csv_name: str, raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return raw_bytes.decode("latin-1")
    except UnicodeDecodeError as exc:
        raise ParseError(
            stage="parse",
            reason=f"Cannot decode {csv_name} as UTF-8 or Latin-1",
        ) from exc


def _parse_csv(text: str, source_file: str, extracted_at: str) -> list[CsvRecord]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    reader = csv.DictReader(io.StringIO(normalized), delimiter="|")
    if reader.fieldnames is None:
        return []

    records: list[CsvRecord] = []
    skipped = 0

    for row in reader:
        if all(v == "" for v in row.values()):
            skipped += 1
            continue
        fields = {k: (v if v is not None else "") for k, v in row.items()}
        records.append(CsvRecord(fields=fields, source_file=source_file, extracted_at=extracted_at))

    if skipped:
        _LOG.debug("Skipped %d empty row(s) in %s", skipped, source_file)

    return records
