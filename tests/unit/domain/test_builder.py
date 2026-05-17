import dataclasses
import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from factor_lib.domain.builder import build_projeto
from factor_lib.domain.exceptions import DomainParseError
from factor_lib.domain.models import (
    Documento,
    ItemPlanoTrabalho,
    MembroEquipe,
    Pagamento,
    PrestacaoContas,
    ProjetoCompleto,
    ProjetoInfo,
    RecursoRubrica,
)
from factor_lib.export.models import CsvRecord


def _rec(source_file: str) -> CsvRecord:
    return CsvRecord(
        fields={"Referência do projeto": "372 - Test"},
        source_file=source_file,
        extracted_at="2026-05-16T14:00:00",
    )


def _make_info() -> ProjetoInfo:
    return ProjetoInfo(
        referencia="372",
        coordenador="Test",
        financiadora="FAPESP",
        data_inicio=datetime.date(2024, 1, 1),
        data_vigencia=datetime.date(2026, 1, 1),
        data_encerramento=None,
        tipo="Pesquisa",
        instituicao_executora="USP",
        departamento=None,
        processo=None,
        valor_aprovado=Decimal("100000"),
        objetivo="Test objetivo",
    )


def _make_membro() -> MembroEquipe:
    return MembroEquipe(
        referencia="372", nome="Ana", funcao="Pesq",
        instituicao=None, vinculo=None, grau_instrucao=None,
        carga_horaria=None, vinculada_executora=False,
    )


def _make_pagamento() -> Pagamento:
    return Pagamento(
        referencia="372", cpf="***", nome_favorecido="X",
        tipo_pagamento="Bolsa", data_pagamento=datetime.date(2024, 3, 1),
        mes_competencia="03/2024", valor=Decimal("1000"),
        tipo_favorecido="pessoa_fisica",
    )


def _make_item() -> ItemPlanoTrabalho:
    return ItemPlanoTrabalho(
        referencia="372", agrupamento=None, rubrica="Bolsas",
        codigo=None, produto=None, descricao=None, justificativa=None,
        qtde_aprovada=None, valor_unitario=None,
        valor_total_aprovado=Decimal("1000"), valor_executado=Decimal("0"),
    )


def _make_recurso() -> RecursoRubrica:
    return RecursoRubrica(
        referencia="372", tipo_rubrica="Despesa", rubrica="Bolsas",
        aprovado=Decimal("1000"), liberado=Decimal("1000"),
        executado=Decimal("0"), moeda="BRL",
    )


def _make_doc() -> Documento:
    return Documento(referencia="372", titulo="Ata", descricao=None)


def _make_prestacao() -> PrestacaoContas:
    return PrestacaoContas(
        referencia="372", titulo="PC1", descricao=None,
        data_inicio=datetime.date(2024, 1, 1),
        data_final=datetime.date(2024, 12, 31),
    )


def test_build_projeto_returns_projeto_completo() -> None:
    records = [_rec("informações do projeto.csv")]
    with (
        patch("factor_lib.domain.builder.parse_project_info", return_value=_make_info()),
        patch("factor_lib.domain.builder.parse_equipe", return_value=[]),
        patch("factor_lib.domain.builder.parse_pagamentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_plano_trabalho", return_value=[]),
        patch("factor_lib.domain.builder.parse_recursos", return_value=[]),
        patch("factor_lib.domain.builder.parse_documentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_prestacoes_contas", return_value=[]),
    ):
        result = build_projeto(records)
    assert isinstance(result, ProjetoCompleto)


def test_build_projeto_result_is_frozen() -> None:
    records = [_rec("informações do projeto.csv")]
    with (
        patch("factor_lib.domain.builder.parse_project_info", return_value=_make_info()),
        patch("factor_lib.domain.builder.parse_equipe", return_value=[_make_membro()]),
        patch("factor_lib.domain.builder.parse_pagamentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_plano_trabalho", return_value=[]),
        patch("factor_lib.domain.builder.parse_recursos", return_value=[]),
        patch("factor_lib.domain.builder.parse_documentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_prestacoes_contas", return_value=[]),
    ):
        result = build_projeto(records)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.info = _make_info()  # type: ignore[misc]


def test_build_projeto_sub_entities_are_tuples() -> None:
    records = [_rec("informações do projeto.csv")]
    membro = _make_membro()
    pagamento = _make_pagamento()
    item = _make_item()
    recurso = _make_recurso()
    doc = _make_doc()
    prestacao = _make_prestacao()
    with (
        patch("factor_lib.domain.builder.parse_project_info", return_value=_make_info()),
        patch("factor_lib.domain.builder.parse_equipe", return_value=[membro]),
        patch("factor_lib.domain.builder.parse_pagamentos", return_value=[pagamento]),
        patch("factor_lib.domain.builder.parse_plano_trabalho", return_value=[item]),
        patch("factor_lib.domain.builder.parse_recursos", return_value=[recurso]),
        patch("factor_lib.domain.builder.parse_documentos", return_value=[doc]),
        patch("factor_lib.domain.builder.parse_prestacoes_contas", return_value=[prestacao]),
    ):
        result = build_projeto(records)
    assert isinstance(result.equipe, tuple)
    assert isinstance(result.pagamentos, tuple)
    assert isinstance(result.plano_trabalho, tuple)
    assert isinstance(result.recursos, tuple)
    assert isinstance(result.documentos, tuple)
    assert isinstance(result.prestacoes_contas, tuple)
    assert len(result.equipe) == 1
    assert len(result.pagamentos) == 1


def test_build_projeto_missing_projeto_info_raises() -> None:
    records = [_rec("equipe.csv")]
    with (
        patch("factor_lib.domain.builder.parse_project_info", side_effect=DomainParseError(
            stage="parse_project_info", reason="no records"
        )),
        patch("factor_lib.domain.builder.parse_equipe", return_value=[]),
        patch("factor_lib.domain.builder.parse_pagamentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_plano_trabalho", return_value=[]),
        patch("factor_lib.domain.builder.parse_recursos", return_value=[]),
        patch("factor_lib.domain.builder.parse_documentos", return_value=[]),
        patch("factor_lib.domain.builder.parse_prestacoes_contas", return_value=[]),
    ):
        with pytest.raises(DomainParseError):
            build_projeto(records)


def test_build_projeto_empty_list_raises() -> None:
    with pytest.raises(DomainParseError):
        build_projeto([])
