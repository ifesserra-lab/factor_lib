"""Exception hierarchy for factor_lib.export."""
from factor_lib.exceptions import FactoLibError


class ExportError(FactoLibError):
    """Raised when the CSV export flow fails at any stage."""

    def __init__(self, *, stage: str, reason: str) -> None:
        self.stage = stage
        self.reason = reason
        super().__init__(f"{stage} stage failed: {reason}")


class DownloadTimeoutError(ExportError):
    """Raised when the ZIP download exceeds the configured timeout."""


class ButtonNotFoundError(ExportError):
    """Raised when 'Exportar em CSV' button is not found on the page."""


class ParseError(ExportError):
    """Raised when the ZIP archive or a CSV within it cannot be parsed."""
