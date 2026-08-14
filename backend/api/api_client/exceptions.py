class APIConnectionError(Exception):
    """Raised when API cannot be reached."""
    pass


class APITimeoutError(Exception):
    """Raised when API request times out."""
    pass


class APIServerError(Exception):
    """Raised when server returns an error."""
    pass


class APIValidationError(Exception):
    """Raised when API validation fails."""
    pass