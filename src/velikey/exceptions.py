"""
VeliKey SDK Exceptions
"""

class VeliKeyError(Exception):
    """Base exception for VeliKey SDK errors."""
    
    def __init__(self, message: str, code: str = None, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class APIError(VeliKeyError):
    """API communication error."""
    pass

class AuthenticationError(VeliKeyError):
    """Authentication failed."""
    pass

class ValidationError(VeliKeyError):
    """Request validation failed."""
    pass

class NotFoundError(VeliKeyError):
    """Resource not found."""
    pass

class RateLimitError(VeliKeyError):
    """Rate limit exceeded."""
    pass

class PolicyConflictError(VeliKeyError):
    """Policy conflict detected."""
    pass

class ThresholdBreachError(VeliKeyError):
    """Threshold breach detected."""
    pass
