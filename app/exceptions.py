class ValidationException(Exception):
    """Raised when data validation fails"""
    pass

class DatabaseException(Exception):
    """Raised when database operations fail"""
    pass

class NotFoundException(Exception):
    """Raised when a requested resource is not found"""
    pass

class ExternalServiceException(Exception):
    """Raised when an external service call fails"""
    pass 