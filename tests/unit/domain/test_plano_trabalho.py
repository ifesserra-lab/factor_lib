from decimal import Decimal

from factor_lib.domain.models import ItemPlanoTrabalho
from factor_lib.domain.parsers.plano_trabalho import parse_plano_trabalho
from factor_lib.export.models import CsvRecord

_AT = "2026-05-16T14:00:00"


def _rec(fields: dict[str, str]) -> CsvRecord:
    return CsvRecord(fields=fields, source_file="plano de trabalho.csv", extracted_at=_AT)


_BASE = {
    "Referência do projeto": "372 - Estudos",
    "Agrupamento": "Equipamentos",
    "Rubrica": "Material permanente",
    "Código": "3.3.90.30",
    "Produto": "Microscópio",
    "Descrição": "Microscópio eletrônico",
    "Justificativa": "Análise de amostras",
    "Qtde aprovada": "2",
    "Valor unitário": "50.000,00",
    "Valor total aprovado": "100.000,00",
    "Valor executado": "0,00",
}


def test_parse_plano_trabalho_returns_list() -> None:
    result = parse_plano_trabalho([_rec(_BASE)])
    assert len(result) == 1
    assert isinstance(result[0], ItemPlanoTrabalho)


def test_parse_plano_trabalho_decimal_fields() -> None:
    result = parse_plano_trabalho([_rec(_BASE)])
    item = result[0]
    assert isinstance(item.valor_total_aprovado, Decimal)
    assert isinstance(item.valor_executado, Decimal)
    assert isinstance(item.valor_unitario, Decimal)
    assert item.valor_total_aprovado == Decimal("100000.00")
    assert item.valor_executado == Decimal("0.00")
    assert item.valor_unitario == Decimal("50000.00")


def test_parse_plano_trabalho_xa0_codigo_is_none() -> None:
    fields = {**_BASE, "Código": "\xa0"}
    result = parse_plano_trabalho([_rec(fields)])
    assert result[0].codigo is None


def test_parse_plano_trabalho_xa0_agrupamento_is_none() -> None:
    fields = {**_BASE, "Agrupamento": ""}
    result = parse_plano_trabalho([_rec(fields)])
    assert result[0].agrupamento is None


def test_parse_plano_trabalho_xa0_produto_is_none() -> None:
    fields = {**_BASE, "Produto": "\xa0"}
    result = parse_plano_trabalho([_rec(fields)])
    assert result[0].produto is None


def test_parse_plano_trabalho_blank_valor_unitario_is_none() -> None:
    fields = {**_BASE, "Valor unitário": "\xa0"}
    result = parse_plano_trabalho([_rec(fields)])
    assert result[0].valor_unitario is None


def test_parse_plano_trabalho_empty_returns_empty() -> None:
    assert parse_plano_trabalho([]) == []


def test_parse_plano_trabalho_filters_non_matching() -> None:
    plano_rec = _rec(_BASE)
    other = CsvRecord(fields={"Rubrica": "X"}, source_file="equipe.csv", extracted_at=_AT)
    result = parse_plano_trabalho([plano_rec, other])
    assert len(result) == 1


def test_parse_plano_trabalho_multiple_records() -> None:
    rec2 = _rec({**_BASE, "Rubrica": "Custeio", "Valor total aprovado": "5.000,00"})
    result = parse_plano_trabalho([_rec(_BASE), rec2])
    assert len(result) == 2
