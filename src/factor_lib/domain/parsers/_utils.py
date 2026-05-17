import datetime
from decimal import Decimal, InvalidOperation

from factor_lib.domain.exceptions import DomainParseError

_EMPTY_VALUES = {"", "\xa0", " "}


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if stripped in _EMPTY_VALUES or stripped == "\xa0":
        return None
    return stripped


def _parse_money(value: str | None) -> Decimal:
    cleaned = _clean(value)
    if cleaned is None:
        return Decimal("0")
    try:
        normalized = cleaned.replace(".", "").replace(",", ".")
        return Decimal(normalized)
    except InvalidOperation:
        return Decimal("0")


def _parse_date(value: str | None) -> datetime.date | None:
    cleaned = _clean(value)
    if cleaned is None:
        return None
    try:
        return datetime.datetime.strptime(cleaned, "%d/%m/%Y").date()
    except ValueError as exc:
        raise DomainParseError(
            stage="parse_date",
            reason=f"invalid date '{cleaned}' — expected DD/MM/YYYY",
        ) from exc


def _parse_ref(value: str | None) -> str:
    cleaned = _clean(value)
    if cleaned is None:
        return ""
    return cleaned.split(" - ")[0].strip()
