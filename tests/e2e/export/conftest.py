"""Shared fixtures for E2E export tests."""
from __future__ import annotations

import io
import zipfile

import pytest


@pytest.fixture()
def sample_zip_bytes() -> bytes:
    """Minimal valid ZIP with one UTF-8 CSV and one Latin-1 CSV."""
    csv_utf8 = "Código,Situação,Valor\nPRJ-001,Em andamento,500000\n"
    csv_latin1_bytes = "Objeto,Exercício\nConstrução de escola,2024\n".encode("latin-1")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("projetos.csv", csv_utf8.encode("utf-8"))
        zf.writestr("detalhes.csv", csv_latin1_bytes)
    return buf.getvalue()
