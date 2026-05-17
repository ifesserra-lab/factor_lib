from __future__ import annotations

from factor_lib.domain.models import RecursoRubrica
from factor_lib.domain.parsers._utils import _clean, _parse_money, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"


def parse_recursos(records: list[CsvRecord]) -> list[RecursoRubrica]:
    matching = [r for r in records if "recurso" in r.source_file.lower()]
    result: list[RecursoRubrica] = []
    for r in matching:
        f = r.fields
        result.append(RecursoRubrica(
            referencia=_parse_ref(f.get(_REF)),
            tipo_rubrica=_clean(f.get("Tipo da Rubrica")) or "",
            rubrica=_clean(f.get("Rubrica")) or "",
            aprovado=_parse_money(f.get("Aprovado")),
            liberado=_parse_money(f.get("Liberado")),
            executado=_parse_money(f.get("Executado")),
            moeda=_clean(f.get("Moeda")) or "",
        ))
    return result
