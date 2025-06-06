class BaseAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(BaseAPIException):
    """Raised when validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class NotFoundException(BaseAPIException):
    """Raised when a resource is not found"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class DatabaseException(BaseAPIException):
    """Raised when database operations fail"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class UnauthorizedException(BaseAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)

class ForbiddenException(BaseAPIException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)

class ConflictException(BaseAPIException):
    """Raised when there's a conflict with existing data"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

class RateLimitException(BaseAPIException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)

class ExternalServiceException(BaseAPIException):
    """Raised when external service calls fail"""
    def __init__(self, message: str):
        super().__init__(message, status_code=502) 