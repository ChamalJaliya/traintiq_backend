"""
Decorators for TraintiQ Backend
Provides logging, validation, and error handling decorators
"""

import functools
import time
import uuid
from typing import Any, Callable, Optional, Dict
from flask import request, g
from .logger import logger_service, RequestLogger

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = f"{func.__module__}.{func.__qualname__}"
        
        logger_service.trace(f"Starting execution: {function_name}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger_service.info(f"Function executed successfully: {function_name}", 
                               execution_time=execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger_service.error(f"Function execution failed: {function_name}", 
                                execution_time=execution_time,
                                error=str(e))
            raise
    
    return wrapper

def handle_exceptions(default_return: Any = None, 
                     log_error: bool = True,
                     reraise: bool = True) -> Callable:
    """Decorator to handle exceptions gracefully"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                function_name = f"{func.__module__}.{func.__qualname__}"
                
                if log_error:
                    logger_service.error(f"Exception in {function_name}: {str(e)}")
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator

def validate_request_data(required_fields: list = None, 
                         optional_fields: list = None) -> Callable:
    """Decorator to validate request data"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'json') or not request.json:
                logger_service.warning("Request validation failed: No JSON data")
                return {"error": "Request must contain JSON data"}, 400
            
            data = request.json
            missing_fields = []
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
            
            if missing_fields:
                logger_service.warning(f"Request validation failed: Missing fields {missing_fields}")
                return {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 400
            
            # Add validated data to kwargs
            kwargs['validated_data'] = data
            
            logger_service.trace("Request validation passed", 
                                required_fields=required_fields,
                                provided_fields=list(data.keys()))
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def with_request_id(func: Callable) -> Callable:
    """Decorator to add request ID to Flask g object and logs"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        
        # Get endpoint name
        endpoint = request.endpoint or func.__name__
        
        # Use request logger context manager
        with RequestLogger(request_id, endpoint):
            return func(*args, **kwargs)
    
    return wrapper

def rate_limit(max_requests: int = 100, 
               time_window: int = 3600,
               storage: Dict = None) -> Callable:
    """Simple rate limiting decorator"""
    if storage is None:
        storage = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            storage[client_ip] = [
                timestamp for timestamp in storage.get(client_ip, [])
                if current_time - timestamp < time_window
            ]
            
            # Check rate limit
            if len(storage.get(client_ip, [])) >= max_requests:
                logger_service.warning(f"Rate limit exceeded for IP: {client_ip}")
                return {"error": "Rate limit exceeded"}, 429
            
            # Add current request
            storage.setdefault(client_ip, []).append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def cache_result(cache_duration: int = 300,
                cache_storage: Dict = None) -> Callable:
    """Simple caching decorator"""
    if cache_storage is None:
        cache_storage = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            current_time = time.time()
            
            # Check if cached result exists and is valid
            if cache_key in cache_storage:
                cached_data, timestamp = cache_storage[cache_key]
                if current_time - timestamp < cache_duration:
                    logger_service.trace(f"Cache hit for: {func.__name__}")
                    return cached_data
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_storage[cache_key] = (result, current_time)
            
            logger_service.trace(f"Cache miss for: {func.__name__}")
            return result
        
        return wrapper
    return decorator

def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication (placeholder for future implementation)"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: Implement actual authentication logic
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger_service.warning("Authentication required but no auth header provided")
            return {"error": "Authentication required"}, 401
        
        # For now, just log the attempt
        logger_service.trace("Authentication check passed (placeholder)")
        
        return func(*args, **kwargs)
    
    return wrapper 