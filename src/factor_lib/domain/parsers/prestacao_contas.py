from __future__ import annotations

import datetime

from factor_lib.domain.models import PrestacaoContas
from factor_lib.domain.parsers._utils import _clean, _parse_date, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"
_TITULO = "Título do Arquivo"
_DESCRICAO = "Descrição"
_DATA_INICIO = "Data início"


def parse_prestacoes_contas(records: list[CsvRecord]) -> list[PrestacaoContas]:
    matching = [r for r in records if "presta" in r.source_file.lower()]
    result: list[PrestacaoContas] = []
    for r in matching:
        f = r.fields
        data_inicio = _parse_date(f.get(_DATA_INICIO))
        data_final = _parse_date(f.get("Data final"))
        result.append(PrestacaoContas(
            referencia=_parse_ref(f.get(_REF)),
            titulo=_clean(f.get(_TITULO)) or "",
            descricao=_clean(f.get(_DESCRICAO)),
            data_inicio=data_inicio or datetime.date.min,
            data_final=data_final or datetime.date.min,
        ))
    return result
