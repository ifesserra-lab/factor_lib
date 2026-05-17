import dataclasses
import datetime
from decimal import Decimal

import pytest

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

# --- ProjetoInfo ---

def _make_projeto_info() -> ProjetoInfo:
    return ProjetoInfo(
        referencia="372",
        coordenador="João Silva",
        financiadora="FAPESP",
        data_inicio=datetime.date(2023, 1, 1),
        data_vigencia=datetime.date(2025, 12, 31),
        data_encerramento=None,
        tipo="Pesquisa",
        instituicao_executora="USP",
        departamento=None,
        processo=None,
        valor_aprovado=Decimal("100000.00"),
        objetivo="Estudar impacto ambiental",
    )


def test_projeto_info_frozen() -> None:
    info = _make_projeto_info()
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.referencia = "999"  # type: ignore[misc]


def test_projeto_info_value_equality() -> None:
    assert _make_projeto_info() == _make_projeto_info()


def test_projeto_info_field_types() -> None:
    info = _make_projeto_info()
    assert isinstance(info.referencia, str)
    assert isinstance(info.data_inicio, datetime.date)
    assert isinstance(info.valor_aprovado, Decimal)
    assert info.departamento is None
    assert info.data_encerramento is None


# --- MembroEquipe ---

def _make_membro() -> MembroEquipe:
    return MembroEquipe(
        referencia="372",
        nome="Maria Costa",
        funcao="Pesquisadora",
        instituicao="USP",
        vinculo="CLT",
        grau_instrucao="Doutorado",
        carga_horaria="20h",
        vinculada_executora=True,
    )


def test_membro_equipe_frozen() -> None:
    m = _make_membro()
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.nome = "Outro"  # type: ignore[misc]


def test_membro_equipe_vinculada_is_bool() -> None:
    m = _make_membro()
    assert isinstance(m.vinculada_executora, bool)
    assert m.vinculada_executora is True


def test_membro_equipe_optional_none() -> None:
    m = MembroEquipe(
        referencia="372",
        nome="Ana",
        funcao="Bolsista",
        instituicao=None,
        vinculo=None,
        grau_instrucao=None,
        carga_horaria=None,
        vinculada_executora=False,
    )
    assert m.instituicao is None
    assert m.carga_horaria is None


# --- Pagamento ---

def _make_pagamento() -> Pagamento:
    return Pagamento(
        referencia="372",
        cpf="***.506.767-**",
        nome_favorecido="Carlos Oliveira",
        tipo_pagamento="Bolsa",
        data_pagamento=datetime.date(2024, 3, 15),
        mes_competencia="03/2024",
        valor=Decimal("2500.00"),
        tipo_favorecido="pessoa_fisica",
    )


def test_pagamento_frozen() -> None:
    p = _make_pagamento()
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.valor = Decimal("0")  # type: ignore[misc]


def test_pagamento_valor_is_decimal() -> None:
    p = _make_pagamento()
    assert isinstance(p.valor, Decimal)


def test_pagamento_data_pagamento_is_date() -> None:
    p = _make_pagamento()
    assert isinstance(p.data_pagamento, datetime.date)


# --- ItemPlanoTrabalho ---

def _make_item_plano() -> ItemPlanoTrabalho:
    return ItemPlanoTrabalho(
        referencia="372",
        agrupamento="Equipamentos",
        rubrica="Material permanente",
        codigo="3.3.90.30",
        produto="Microscópio",
        descricao="Microscópio eletrônico",
        justificativa="Análise de amostras",
        qtde_aprovada="2",
        valor_unitario=Decimal("50000.00"),
        valor_total_aprovado=Decimal("100000.00"),
        valor_executado=Decimal("0.00"),
    )


def test_item_plano_frozen() -> None:
    item = _make_item_plano()
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.rubrica = "X"  # type: ignore[misc]


def test_item_plano_decimal_fields() -> None:
    item = _make_item_plano()
    assert isinstance(item.valor_total_aprovado, Decimal)
    assert isinstance(item.valor_executado, Decimal)
    assert isinstance(item.valor_unitario, Decimal)


def test_item_plano_optional_none() -> None:
    item = ItemPlanoTrabalho(
        referencia="372",
        agrupamento=None,
        rubrica="Custeio",
        codigo=None,
        produto=None,
        descricao=None,
        justificativa=None,
        qtde_aprovada=None,
        valor_unitario=None,
        valor_total_aprovado=Decimal("1000.00"),
        valor_executado=Decimal("0.00"),
    )
    assert item.codigo is None
    assert item.valor_unitario is None


# --- RecursoRubrica ---

def _make_recurso() -> RecursoRubrica:
    return RecursoRubrica(
        referencia="372",
        tipo_rubrica="Despesa",
        rubrica="Material de consumo",
        aprovado=Decimal("5000.00"),
        liberado=Decimal("5000.00"),
        executado=Decimal("3000.00"),
        moeda="BRL",
    )


def test_recurso_frozen() -> None:
    r = _make_recurso()
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.aprovado = Decimal("0")  # type: ignore[misc]


def test_recurso_decimal_fields() -> None:
    r = _make_recurso()
    assert isinstance(r.aprovado, Decimal)
    assert isinstance(r.liberado, Decimal)
    assert isinstance(r.executado, Decimal)


# --- Documento ---

def test_documento_frozen() -> None:
    d = Documento(referencia="372", titulo="Ata", descricao=None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.titulo = "X"  # type: ignore[misc]


def test_documento_optional_descricao() -> None:
    d = Documento(referencia="372", titulo="Ata", descricao=None)
    assert d.descricao is None


# --- PrestacaoContas ---

def _make_prestacao() -> PrestacaoContas:
    return PrestacaoContas(
        referencia="372",
        titulo="Relatório anual",
        descricao=None,
        data_inicio=datetime.date(2024, 1, 1),
        data_final=datetime.date(2024, 12, 31),
    )


def test_prestacao_frozen() -> None:
    pc = _make_prestacao()
    with pytest.raises(dataclasses.FrozenInstanceError):
        pc.titulo = "X"  # type: ignore[misc]


def test_prestacao_dates_are_date() -> None:
    pc = _make_prestacao()
    assert isinstance(pc.data_inicio, datetime.date)
    assert isinstance(pc.data_final, datetime.date)


# --- ProjetoCompleto ---

def _make_projeto_completo() -> ProjetoCompleto:
    return ProjetoCompleto(
        info=_make_projeto_info(),
        equipe=(_make_membro(),),
        documentos=(Documento(referencia="372", titulo="Ata", descricao=None),),
        pagamentos=(_make_pagamento(),),
        plano_trabalho=(_make_item_plano(),),
        recursos=(_make_recurso(),),
        prestacoes_contas=(_make_prestacao(),),
    )


def test_projeto_completo_frozen() -> None:
    pc = _make_projeto_completo()
    with pytest.raises(dataclasses.FrozenInstanceError):
        pc.info = _make_projeto_info()  # type: ignore[misc]


def test_projeto_completo_sub_entity_types() -> None:
    pc = _make_projeto_completo()
    assert isinstance(pc.info, ProjetoInfo)
    assert isinstance(pc.equipe, tuple)
    assert isinstance(pc.pagamentos, tuple)
    assert isinstance(pc.plano_trabalho, tuple)
    assert isinstance(pc.recursos, tuple)
    assert isinstance(pc.documentos, tuple)
    assert isinstance(pc.prestacoes_contas, tuple)
