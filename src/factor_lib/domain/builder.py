from __future__ import annotations

from factor_lib.domain.models import ProjetoCompleto
from factor_lib.domain.parsers.documentos import parse_documentos
from factor_lib.domain.parsers.equipe import parse_equipe
from factor_lib.domain.parsers.pagamentos import parse_pagamentos
from factor_lib.domain.parsers.plano_trabalho import parse_plano_trabalho
from factor_lib.domain.parsers.prestacao_contas import parse_prestacoes_contas
from factor_lib.domain.parsers.projeto_info import parse_project_info
from factor_lib.domain.parsers.recursos import parse_recursos
from factor_lib.export.models import CsvRecord


def build_projeto(records: list[CsvRecord]) -> ProjetoCompleto:
    info = parse_project_info(records)
    return ProjetoCompleto(
        info=info,
        equipe=tuple(parse_equipe(records)),
        documentos=tuple(parse_documentos(records)),
        pagamentos=tuple(parse_pagamentos(records)),
        plano_trabalho=tuple(parse_plano_trabalho(records)),
        recursos=tuple(parse_recursos(records)),
        prestacoes_contas=tuple(parse_prestacoes_contas(records)),
    )
