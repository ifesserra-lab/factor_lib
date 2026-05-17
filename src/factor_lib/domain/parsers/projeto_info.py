from __future__ import annotations

from factor_lib.domain.exceptions import DomainParseError
from factor_lib.domain.models import ProjetoInfo
from factor_lib.domain.parsers._utils import _clean, _parse_date, _parse_money, _parse_ref
from factor_lib.export.models import CsvRecord

_DATA_INICIO = "Data de início"
_DATA_VIGENCIA = "Data de vigência"
_INST_EXEC = "Instituição executora"
_OBJETIVO = "Objetivo/Objeto/Título"


def parse_project_info(records: list[CsvRecord]) -> ProjetoInfo:
    matching = [r for r in records if "informa" in r.source_file.lower()]
    if not matching:
        raise DomainParseError(
            stage="parse_project_info",
            reason="no 'informações do projeto' records found",
        )
    f = matching[0].fields
    return ProjetoInfo(
        referencia=_parse_ref(f.get("Referência do projeto")),
        coordenador=_clean(f.get("Coordenador")) or "",
        financiadora=_clean(f.get("Financiadora")) or "",
        data_inicio=_parse_date(f.get(_DATA_INICIO)),  # type: ignore[arg-type]
        data_vigencia=_parse_date(f.get(_DATA_VIGENCIA)),  # type: ignore[arg-type]
        data_encerramento=_parse_date(f.get("Data de encerramento")),
        tipo=_clean(f.get("Tipo de Projeto")) or "",
        instituicao_executora=_clean(f.get(_INST_EXEC)) or "",
        departamento=_clean(f.get("Departamento")),
        processo=_clean(f.get("Processo e sub-processo")),
        valor_aprovado=_parse_money(f.get("Valor aprovado")),
        objetivo=_clean(f.get(_OBJETIVO)) or "",
    )
