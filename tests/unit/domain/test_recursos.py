from decimal import Decimal

from factor_lib.domain.models import RecursoRubrica
from factor_lib.domain.parsers.recursos import parse_recursos
from factor_lib.export.models import CsvRecord


def _rec(fields: dict[str, str]) -> CsvRecord:
    return CsvRecord(
        fields=fields,
        source_file="recursos por rubrica receita separada.csv",
        extracted_at="2026-05-16T14:00:00",
    )


_BASE = {
    "Referência do projeto": "372 - Estudos",
    "Tipo da Rubrica": "Despesa",
    "Rubrica": "Bolsas",
    "Aprovado": "3.722.800,00",
    "Liberado": "3.722.800,00",
    "Executado": "1.000.000,00",
    "Moeda": "BRL",
}


def test_parse_recursos_returns_list() -> None:
    result = parse_recursos([_rec(_BASE)])
    assert len(result) == 1
    assert isinstance(result[0], RecursoRubrica)


def test_parse_recursos_decimal_fields() -> None:
    result = parse_recursos([_rec(_BASE)])
    r = result[0]
    assert isinstance(r.aprovado, Decimal)
    assert isinstance(r.liberado, Decimal)
    assert isinstance(r.executado, Decimal)
    assert r.aprovado == Decimal("3722800.00")
    assert r.executado == Decimal("1000000.00")


def test_parse_recursos_moeda_stored_as_is() -> None:
    result = parse_recursos([_rec(_BASE)])
    assert result[0].moeda == "BRL"


def test_parse_recursos_empty_returns_empty() -> None:
    assert parse_recursos([]) == []


def test_parse_recursos_filters_non_matching() -> None:
    rec = _rec(_BASE)
    other = CsvRecord(
        fields={"Rubrica": "X"}, source_file="equipe.csv", extracted_at="2026-05-16T14:00:00"
    )
    result = parse_recursos([rec, other])
    assert len(result) == 1


def test_parse_recursos_multiple_records() -> None:
    rec2 = _rec({**_BASE, "Rubrica": "Custeio", "Aprovado": "5.000,00"})
    result = parse_recursos([_rec(_BASE), rec2])
    assert len(result) == 2
