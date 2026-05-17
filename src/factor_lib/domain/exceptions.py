from factor_lib.exceptions import FactoLibError


class DomainParseError(FactoLibError):
    def __init__(self, *, stage: str, reason: str) -> None:
        self.stage = stage
        self.reason = reason
        super().__init__(f"{stage}: {reason}")
