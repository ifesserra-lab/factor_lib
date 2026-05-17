import datetime
from decimal import Decimal

import pytest

from factor_lib.domain.exceptions import DomainParseError
from factor_lib.domain.models import ProjetoInfo
from factor_lib.domain.parsers.projeto_info import parse_project_info
from factor_lib.export.models import CsvRecord


def _make_record(
    fields: dict[str, str], source_file: str = "informações do projeto.csv"
) -> CsvRecord:
    return CsvRecord(fields=fields, source_file=source_file, extracted_at="2026-05-16T14:00:00")


_FULL_FIELDS = {
    "Referência do projeto": "372 - Estudos de Impacto",
    "Coordenador": "Alexandre Chahad",
    "Financiadora": "Ministério dos Povos Indígenas (MPI)",
    "Data de início": "07/04/2026",
    "Data de vigência": "07/12/2026",
    "Data de encerramento": "07/02/2027",
    "Tipo de Projeto": "Pesquisa, Desenvolvimento e Inovação",
    "Instituição executora": "Instituto Federal De Educação Ciência E Tecnologia",
    "Departamento": "Ciências Humanas",
    "Processo e sub-processo": "01234567/2026",
    "Valor aprovado": "3.722.800,00",
    "Objetivo/Objeto/Título": "Estudar o impacto socioambiental.",
}


def test_parse_project_info_returns_projeto_info() -> None:
    records = [_make_record(_FULL_FIELDS)]
    result = parse_project_info(records)
    assert isinstance(result, ProjetoInfo)


def test_parse_project_info_referencia_normalized() -> None:
    records = [_make_record(_FULL_FIELDS)]
    result = parse_project_info(records)
    assert result.referencia == "372"


def test_parse_project_info_string_fields() -> None:
    records = [_make_record(_FULL_FIELDS)]
    result = parse_project_info(records)
    assert result.coordenador == "Alexandre Chahad"
    assert result.financiadora == "Ministério dos Povos Indígenas (MPI)"
    assert result.tipo == "Pesquisa, Desenvolvimento e Inovação"
    assert result.instituicao_executora == "Instituto Federal De Educação Ciência E Tecnologia"


def test_parse_project_info_date_fields_are_date() -> None:
    records = [_make_record(_FULL_FIELDS)]
    result = parse_project_info(records)
    assert result.data_inicio == datetime.date(2026, 4, 7)
    assert result.data_vigencia == datetime.date(2026, 12, 7)
    assert result.data_encerramento == datetime.date(2027, 2, 7)


def test_parse_project_info_valor_is_decimal() -> None:
    records = [_make_record(_FULL_FIELDS)]
    result = parse_project_info(records)
    assert isinstance(result.valor_aprovado, Decimal)
    assert result.valor_aprovado == Decimal("3722800.00")


def test_parse_project_info_optional_encerramento_none_when_xa0() -> None:
    fields = {**_FULL_FIELDS, "Data de encerramento": "\xa0"}
    records = [_make_record(fields)]
    result = parse_project_info(records)
    assert result.data_encerramento is None


def test_parse_project_info_optional_departamento_none_when_xa0() -> None:
    fields = {**_FULL_FIELDS, "Departamento": "\xa0"}
    records = [_make_record(fields)]
    result = parse_project_info(records)
    assert result.departamento is None


def test_parse_project_info_optional_processo_none_when_empty() -> None:
    fields = {**_FULL_FIELDS, "Processo e sub-processo": ""}
    records = [_make_record(fields)]
    result = parse_project_info(records)
    assert result.processo is None


def test_parse_project_info_filters_by_source_file() -> None:
    info_record = _make_record(_FULL_FIELDS, "informações do projeto.csv")
    other_record = _make_record({"Referência do projeto": "000"}, "equipe.csv")
    result = parse_project_info([info_record, other_record])
    assert result.referencia == "372"


def test_parse_project_info_empty_list_raises() -> None:
    with pytest.raises(DomainParseError):
        parse_project_info([])


def test_parse_project_info_no_matching_source_file_raises() -> None:
    records = [_make_record({"Referência do projeto": "999"}, "equipe.csv")]
    with pytest.raises(DomainParseError):
        parse_project_info(records)


def test_parse_project_info_keyword_matches_encoded_filename() -> None:
    # source_file as it appears from latin-1/CP437 encoded ZIP
    fields = _FULL_FIELDS
    record = _make_record(fields, "informa‡oes do projeto.csv")
    result = parse_project_info([record])
    assert result.referencia == "372"
