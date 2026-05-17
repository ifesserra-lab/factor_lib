from __future__ import annotations

from factor_lib.domain.models import MembroEquipe
from factor_lib.domain.parsers._utils import _clean, _parse_ref
from factor_lib.export.models import CsvRecord

_REF = "Referência do projeto"
_FUNCAO = "Função"
_INSTITUICAO = "Instituição de trabalho"
_VINCULO = "Vínculo com a instituição"
_GRAU = "Grau de instrução"
_CARGA = "Carga horária"
_VINCULADA = "Vinculada à inst. executora"


def parse_equipe(records: list[CsvRecord]) -> list[MembroEquipe]:
    matching = [r for r in records if "equipe" in r.source_file.lower()]
    result: list[MembroEquipe] = []
    for r in matching:
        f = r.fields
        vinculada_raw = _clean(f.get(_VINCULADA, ""))
        result.append(MembroEquipe(
            referencia=_parse_ref(f.get(_REF)),
            nome=_clean(f.get("Nome")) or "",
            funcao=_clean(f.get(_FUNCAO)) or "",
            instituicao=_clean(f.get(_INSTITUICAO)),
            vinculo=_clean(f.get(_VINCULO)),
            grau_instrucao=_clean(f.get(_GRAU)),
            carga_horaria=_clean(f.get(_CARGA)),
            vinculada_executora=(vinculada_raw == "Sim"),
        ))
    return result
