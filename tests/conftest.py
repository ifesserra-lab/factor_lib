"""Shared pytest fixtures for unit and integration tests."""
from __future__ import annotations

import pytest


@pytest.fixture()
def portal_url() -> str:
    return "https://facto.conveniar.com.br/portaltransparencia/"
