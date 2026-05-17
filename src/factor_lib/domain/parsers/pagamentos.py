from __future__ import annotations

from factor_lib.domain.models import Pagamento
from factor_lib.domain.parsers._utils import _clean, _parse_date, _parse_money, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"
_MES = "Mês de Competência"


def _tipo_favorecido(source_file: str) -> str:
    sf = source_file.lower()
    if "pessoa" in sf:
        return "pessoa_fisica"
    return "servidor"


def parse_pagamentos(records: list[CsvRecord]) -> list[Pagamento]:
    matching = [r for r in records if "pagamento" in r.source_file.lower()]
    result: list[Pagamento] = []
    for r in matching:
        f = r.fields
        data = _parse_date(f.get("Data do Pagamento"))
        result.append(Pagamento(
            referencia=_parse_ref(f.get(_REF)),
            cpf=_clean(f.get("CPF")) or "",
            nome_favorecido=_clean(f.get("Nome do Favorecido")) or "",
            tipo_pagamento=_clean(f.get("Tipo de Pagamento")) or "",
            data_pagamento=data or __import__("datetime").date.min,
            mes_competencia=_clean(f.get(_MES)) or "",
            valor=_parse_money(f.get("Valor")),
            tipo_favorecido=_tipo_favorecido(r.source_file),
        ))
    return result
