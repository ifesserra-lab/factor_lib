
from factor_lib.domain.models import MembroEquipe
from factor_lib.domain.parsers.equipe import parse_equipe
from factor_lib.export.models import CsvRecord


def _rec(fields: dict[str, str]) -> CsvRecord:
    return CsvRecord(fields=fields, source_file="equipe.csv", extracted_at="2026-05-16T14:00:00")


_BASE_FIELDS = {
    "Referência do projeto": "372 - Estudos",
    "Nome": "Maria Costa",
    "Função": "Pesquisadora",
    "Instituição de trabalho": "USP",
    "Vínculo com a instituição": "CLT",
    "Grau de instrução": "Doutorado",
    "Carga horária": "20h",
    "Vinculada à inst. executora": "Sim",
}


def test_parse_equipe_returns_list_of_membro() -> None:
    result = parse_equipe([_rec(_BASE_FIELDS)])
    assert len(result) == 1
    assert isinstance(result[0], MembroEquipe)


def test_parse_equipe_sim_is_true() -> None:
    result = parse_equipe([_rec(_BASE_FIELDS)])
    assert result[0].vinculada_executora is True


def test_parse_equipe_nao_is_false() -> None:
    fields = {**_BASE_FIELDS, "Vinculada à inst. executora": "Não"}
    result = parse_equipe([_rec(fields)])
    assert result[0].vinculada_executora is False


def test_parse_equipe_other_value_is_false() -> None:
    fields = {**_BASE_FIELDS, "Vinculada à inst. executora": ""}
    result = parse_equipe([_rec(fields)])
    assert result[0].vinculada_executora is False


def test_parse_equipe_xa0_fields_are_none() -> None:
    fields = {
        **_BASE_FIELDS,
        "Instituição de trabalho": "\xa0",
        "Vínculo com a instituição": "\xa0",
        "Grau de instrução": "\xa0",
        "Carga horária": "\xa0",
    }
    result = parse_equipe([_rec(fields)])
    m = result[0]
    assert m.instituicao is None
    assert m.vinculo is None
    assert m.grau_instrucao is None
    assert m.carga_horaria is None


def test_parse_equipe_empty_list_returns_empty() -> None:
    assert parse_equipe([]) == []


def test_parse_equipe_filters_non_equipe_records() -> None:
    equipe_rec = _rec(_BASE_FIELDS)
    other_rec = CsvRecord(
        fields={"Nome": "João"},
        source_file="documentos.csv",
        extracted_at="2026-05-16T14:00:00",
    )
    result = parse_equipe([equipe_rec, other_rec])
    assert len(result) == 1


def test_parse_equipe_multiple_records() -> None:
    rec2 = _rec({**_BASE_FIELDS, "Nome": "Ana Lima", "Função": "Coordenadora"})
    result = parse_equipe([_rec(_BASE_FIELDS), rec2])
    assert len(result) == 2
    names = {m.nome for m in result}
    assert "Maria Costa" in names
    assert "Ana Lima" in names
