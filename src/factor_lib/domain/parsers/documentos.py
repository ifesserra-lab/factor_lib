from __future__ import annotations

from factor_lib.domain.models import Documento
from factor_lib.domain.parsers._utils import _clean, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"
_TITULO = "Título do Arquivo"
_DESCRICAO = "Descrição"


def parse_documentos(records: list[CsvRecord]) -> list[Documento]:
    matching = [r for r in records if "documento" in r.source_file.lower()]
    result: list[Documento] = []
    for r in matching:
        f = r.fields
        result.append(Documento(
            referencia=_parse_ref(f.get(_REF)),
            titulo=_clean(f.get(_TITULO)) or "",
            descricao=_clean(f.get(_DESCRICAO)),
        ))
    return result
