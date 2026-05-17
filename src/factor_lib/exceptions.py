"""Base exception hierarchy for factor_lib."""


class FactoLibError(Exception):
    """Base exception for all factor_lib errors."""


class PortalNavigationError(FactoLibError):
    """Raised when browser automation cannot find or interact with a portal element."""
