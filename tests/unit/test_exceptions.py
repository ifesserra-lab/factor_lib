"""Unit tests for PortalNavigationError (T006 — RED)."""
from __future__ import annotations

import pytest

from factor_lib.exceptions import FactoLibError, PortalNavigationError


def test_portal_navigation_error_is_facto_lib_error() -> None:
    assert issubclass(PortalNavigationError, FactoLibError)


def test_portal_navigation_error_carries_message() -> None:
    err = PortalNavigationError("Consultar button not found")
    assert "Consultar button not found" in str(err)


def test_portal_navigation_error_can_be_raised_and_caught() -> None:
    with pytest.raises(PortalNavigationError, match="timeout"):
        raise PortalNavigationError("timeout after 30s")
