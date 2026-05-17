from __future__ import annotations

from decimal import Decimal

from factor_lib.domain.models import ItemPlanoTrabalho
from factor_lib.domain.parsers._utils import _clean, _parse_money, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"
_CODIGO = "Código"
_DESCRICAO = "Descrição"
_VALOR_UNIT = "Valor unitário"


def _parse_money_optional(value: str | None) -> Decimal | None:
    from factor_lib.domain.parsers._utils import _clean as clean
    if clean(value) is None:
        return None
    return _parse_money(value)


def parse_plano_trabalho(records: list[CsvRecord]) -> list[ItemPlanoTrabalho]:
    matching = [r for r in records if "plano" in r.source_file.lower()]
    result: list[ItemPlanoTrabalho] = []
    for r in matching:
        f = r.fields
        valor_unit_raw = f.get(_VALOR_UNIT)
        result.append(ItemPlanoTrabalho(
            referencia=_parse_ref(f.get(_REF)),
            agrupamento=_clean(f.get("Agrupamento")),
            rubrica=_clean(f.get("Rubrica")) or "",
            codigo=_clean(f.get(_CODIGO)),
            produto=_clean(f.get("Produto")),
            descricao=_clean(f.get(_DESCRICAO)),
            justificativa=_clean(f.get("Justificativa")),
            qtde_aprovada=_clean(f.get("Qtde aprovada")),
            valor_unitario=_parse_money_optional(valor_unit_raw),
            valor_total_aprovado=_parse_money(f.get("Valor total aprovado")),
            valor_executado=_parse_money(f.get("Valor executado")),
        ))
    return result
