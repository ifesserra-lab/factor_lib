import datetime
from decimal import Decimal

from factor_lib.domain.models import Pagamento
from factor_lib.domain.parsers.pagamentos import parse_pagamentos
from factor_lib.export.models import CsvRecord


def _rec(fields: dict[str, str], source_file: str) -> CsvRecord:
    return CsvRecord(fields=fields, source_file=source_file, extracted_at="2026-05-16T14:00:00")


_PF_FIELDS = {
    "Referência do projeto": "372 - Estudos",
    "CPF": "***.506.767-**",
    "Nome do Favorecido": "Adilson Prado",
    "Tipo de Pagamento": "Bolsa Estímulo",
    "Data do Pagamento": "15/03/2024",
    "Mês de Competência": "03/2024",
    "Valor": "2.500,00",
}

_SRV_FIELDS = {
    "Referência do projeto": "372 - Estudos",
    "CPF": "***.603.078-**",
    "Nome do Favorecido": "Alexandre Chahad",
    "Tipo de Pagamento": "Bolsa Estímulo",
    "Data do Pagamento": "20/04/2024",
    "Mês de Competência": "04/2024",
    "Valor": "3.722.800,00",
}


def test_parse_pagamentos_pessoa_fisica_tipo() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa física.csv")]
    result = parse_pagamentos(records)
    assert len(result) == 1
    assert result[0].tipo_favorecido == "pessoa_fisica"


def test_parse_pagamentos_servidor_tipo() -> None:
    records = [_rec(_SRV_FIELDS, "pagamento de servidores ou agentes públicos.csv")]
    result = parse_pagamentos(records)
    assert len(result) == 1
    assert result[0].tipo_favorecido == "servidor"


def test_parse_pagamentos_encoded_filename_pessoa_fisica() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa f\xa1sica.csv")]
    result = parse_pagamentos(records)
    assert result[0].tipo_favorecido == "pessoa_fisica"


def test_parse_pagamentos_encoded_filename_servidor() -> None:
    records = [_rec(_SRV_FIELDS, "pagamento de servidores ou agentes p￣blicos.csv")]
    result = parse_pagamentos(records)
    assert result[0].tipo_favorecido == "servidor"


def test_parse_pagamentos_valor_is_decimal() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa física.csv")]
    result = parse_pagamentos(records)
    assert isinstance(result[0].valor, Decimal)
    assert result[0].valor == Decimal("2500.00")


def test_parse_pagamentos_large_valor_decimal() -> None:
    records = [_rec(_SRV_FIELDS, "pagamento de servidores ou agentes públicos.csv")]
    result = parse_pagamentos(records)
    assert result[0].valor == Decimal("3722800.00")


def test_parse_pagamentos_cpf_stored_as_is() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa física.csv")]
    result = parse_pagamentos(records)
    assert result[0].cpf == "***.506.767-**"


def test_parse_pagamentos_data_pagamento_is_date() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa física.csv")]
    result = parse_pagamentos(records)
    assert isinstance(result[0].data_pagamento, datetime.date)
    assert result[0].data_pagamento == datetime.date(2024, 3, 15)


def test_parse_pagamentos_merges_both_sources() -> None:
    pf = _rec(_PF_FIELDS, "pagamento de pessoa física.csv")
    srv = _rec(_SRV_FIELDS, "pagamento de servidores ou agentes públicos.csv")
    result = parse_pagamentos([pf, srv])
    assert len(result) == 2
    tipos = {r.tipo_favorecido for r in result}
    assert tipos == {"pessoa_fisica", "servidor"}


def test_parse_pagamentos_empty_returns_empty() -> None:
    assert parse_pagamentos([]) == []


def test_parse_pagamentos_filters_non_pagamento_records() -> None:
    pf = _rec(_PF_FIELDS, "pagamento de pessoa física.csv")
    other = _rec({"Nome": "X"}, "equipe.csv")
    result = parse_pagamentos([pf, other])
    assert len(result) == 1


def test_parse_pagamentos_returns_list_of_pagamento() -> None:
    records = [_rec(_PF_FIELDS, "pagamento de pessoa física.csv")]
    result = parse_pagamentos(records)
    assert isinstance(result[0], Pagamento)
