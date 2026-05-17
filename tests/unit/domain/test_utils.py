import datetime
from decimal import Decimal

import pytest

from factor_lib.domain.parsers._utils import _clean, _parse_date, _parse_money

# --- _clean ---

@pytest.mark.parametrize("value,expected", [
    (None, None),
    ("", None),
    ("\xa0", None),
    ("  ", None),
    ("  \xa0  ", None),
    ("hello", "hello"),
    ("  hello  ", "hello"),
    ("0", "0"),
])
def test_clean(value: str | None, expected: str | None) -> None:
    assert _clean(value) == expected


# --- _parse_money ---

@pytest.mark.parametrize("value,expected", [
    ("3.722.800,00", Decimal("3722800.00")),
    ("1.234,56", Decimal("1234.56")),
    ("500,00", Decimal("500.00")),
    ("0,00", Decimal("0.00")),
    ("100", Decimal("100")),
])
def test_parse_money_valid(value: str, expected: Decimal) -> None:
    assert _parse_money(value) == expected


def test_parse_money_xa0_returns_zero() -> None:
    assert _parse_money("\xa0") == Decimal("0")


def test_parse_money_empty_returns_zero() -> None:
    assert _parse_money("") == Decimal("0")


def test_parse_money_returns_decimal_not_float() -> None:
    result = _parse_money("1.234,56")
    assert isinstance(result, Decimal)


# --- _parse_date ---

@pytest.mark.parametrize("value,expected", [
    ("07/04/2026", datetime.date(2026, 4, 7)),
    ("01/01/2023", datetime.date(2023, 1, 1)),
    ("31/12/2024", datetime.date(2024, 12, 31)),
])
def test_parse_date_valid(value: str, expected: datetime.date) -> None:
    assert _parse_date(value) == expected


def test_parse_date_xa0_returns_none() -> None:
    assert _parse_date("\xa0") is None


def test_parse_date_empty_returns_none() -> None:
    assert _parse_date("") is None


def test_parse_date_none_returns_none() -> None:
    assert _parse_date(None) is None


def test_parse_date_invalid_format_raises() -> None:
    from factor_lib.domain.exceptions import DomainParseError
    with pytest.raises(DomainParseError):
        _parse_date("2026-04-07")


def test_parse_date_returns_date_not_datetime() -> None:
    result = _parse_date("07/04/2026")
    assert isinstance(result, datetime.date)
    assert not isinstance(result, datetime.datetime)
