import pytest

from factor_lib.domain.exceptions import DomainParseError
from factor_lib.exceptions import FactoLibError


def test_domain_parse_error_is_facto_lib_error() -> None:
    err = DomainParseError(stage="parse", reason="missing field")
    assert isinstance(err, FactoLibError)


def test_domain_parse_error_attributes() -> None:
    err = DomainParseError(stage="parse", reason="missing field")
    assert err.stage == "parse"
    assert err.reason == "missing field"


def test_domain_parse_error_str_contains_stage_and_reason() -> None:
    err = DomainParseError(stage="build", reason="no projeto info")
    assert "build" in str(err)
    assert "no projeto info" in str(err)


def test_domain_parse_error_is_exception() -> None:
    with pytest.raises(DomainParseError):
        raise DomainParseError(stage="test", reason="boom")
