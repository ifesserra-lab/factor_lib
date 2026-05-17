import dataclasses
import datetime
from decimal import Decimal


@dataclasses.dataclass(frozen=True)
class ProjetoInfo:
    referencia: str
    coordenador: str
    financiadora: str
    data_inicio: datetime.date
    data_vigencia: datetime.date
    data_encerramento: datetime.date | None
    tipo: str
    instituicao_executora: str
    departamento: str | None
    processo: str | None
    valor_aprovado: Decimal
    objetivo: str


@dataclasses.dataclass(frozen=True)
class MembroEquipe:
    referencia: str
    nome: str
    funcao: str
    instituicao: str | None
    vinculo: str | None
    grau_instrucao: str | None
    carga_horaria: str | None
    vinculada_executora: bool


@dataclasses.dataclass(frozen=True)
class Pagamento:
    referencia: str
    cpf: str
    nome_favorecido: str
    tipo_pagamento: str
    data_pagamento: datetime.date
    mes_competencia: str
    valor: Decimal
    tipo_favorecido: str


@dataclasses.dataclass(frozen=True)
class ItemPlanoTrabalho:
    referencia: str
    agrupamento: str | None
    rubrica: str
    codigo: str | None
    produto: str | None
    descricao: str | None
    justificativa: str | None
    qtde_aprovada: str | None
    valor_unitario: Decimal | None
    valor_total_aprovado: Decimal
    valor_executado: Decimal


@dataclasses.dataclass(frozen=True)
class RecursoRubrica:
    referencia: str
    tipo_rubrica: str
    rubrica: str
    aprovado: Decimal
    liberado: Decimal
    executado: Decimal
    moeda: str


@dataclasses.dataclass(frozen=True)
class Documento:
    referencia: str
    titulo: str
    descricao: str | None


@dataclasses.dataclass(frozen=True)
class PrestacaoContas:
    referencia: str
    titulo: str
    descricao: str | None
    data_inicio: datetime.date
    data_final: datetime.date


@dataclasses.dataclass(frozen=True)
class ProjetoCompleto:
    info: ProjetoInfo
    equipe: tuple[MembroEquipe, ...]
    documentos: tuple[Documento, ...]
    pagamentos: tuple[Pagamento, ...]
    plano_trabalho: tuple[ItemPlanoTrabalho, ...]
    recursos: tuple[RecursoRubrica, ...]
    prestacoes_contas: tuple[PrestacaoContas, ...]
