from decimal import Decimal

from factor_lib.domain.builder import build_projeto
from factor_lib.domain.models import ProjetoCompleto
from factor_lib.export.models import CsvRecord


def test_build_projeto_returns_projeto_completo(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert isinstance(result, ProjetoCompleto)


def test_build_projeto_referencia(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert result.info.referencia == "372"


def test_build_projeto_equipe_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.equipe) == 19


def test_build_projeto_pagamentos_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.pagamentos) == 21


def test_build_projeto_plano_trabalho_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.plano_trabalho) == 185


def test_build_projeto_recursos_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.recursos) == 11


def test_build_projeto_documentos_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.documentos) == 1


def test_build_projeto_prestacoes_count(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert len(result.prestacoes_contas) == 1


def test_build_projeto_pagamentos_valor_is_decimal(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    for p in result.pagamentos:
        assert isinstance(p.valor, Decimal), f"valor not Decimal for {p.nome_favorecido}"


def test_build_projeto_no_xa0_in_equipe(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    for m in result.equipe:
        for field in (m.instituicao, m.vinculo, m.grau_instrucao, m.carga_horaria):
            if field is not None:
                assert "\xa0" not in field, f"Found \\xa0 in equipe field: {field!r}"


def test_build_projeto_no_xa0_in_plano_trabalho(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    for item in result.plano_trabalho:
        for field in (item.codigo, item.produto, item.descricao, item.justificativa):
            if field is not None:
                assert "\xa0" not in field, f"Found \\xa0 in plano field: {field!r}"


def test_build_projeto_pagamentos_decimal_sum(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    total = sum(p.valor for p in result.pagamentos)
    assert isinstance(total, Decimal)
    assert total > Decimal("0")


def test_build_projeto_info_data_inicio_is_date(real_records: list[CsvRecord]) -> None:
    import datetime
    result = build_projeto(real_records)
    assert isinstance(result.info.data_inicio, datetime.date)
    assert not isinstance(result.info.data_inicio, datetime.datetime)


def test_build_projeto_info_valor_aprovado_is_decimal(real_records: list[CsvRecord]) -> None:
    result = build_projeto(real_records)
    assert isinstance(result.info.valor_aprovado, Decimal)
    assert result.info.valor_aprovado > Decimal("0")
