"""Fixtures for domain integration tests using real data/Projeto_372/ CSV files."""
from __future__ import annotations

import io
import os
import zipfile

import pytest

from factor_lib.export.csv_parser import parse_zip_csv
from factor_lib.export.models import CsvRecord


def _build_zip_from_dir(dirpath: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for filename in os.listdir(dirpath):
            if filename.lower().endswith(".csv"):
                zf.write(os.path.join(dirpath, filename), filename)
    return buf.getvalue()


@pytest.fixture(scope="session")
def real_records() -> list[CsvRecord]:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "Projeto_372")
    zip_bytes = _build_zip_from_dir(data_dir)
    return parse_zip_csv(zip_bytes)
