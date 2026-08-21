class ProfitLensError(Exception):
    """
    Base exception for expected ProfitLens errors.
    """


class InvalidRequestError(ProfitLensError):
    """
    Raised when the request is malformed or invalid.
    """


class ResourceNotFoundError(ProfitLensError):
    """
    Raised when requested business data does not exist.
    """