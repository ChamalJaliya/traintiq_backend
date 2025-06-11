"""
Base Service Class for TraintiQ Backend
Provides common functionality and dependency injection patterns
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from .logger import logger_service

T = TypeVar('T')

class BaseService(ABC):
    """
    Abstract base service class providing common functionality
    """
    
    def __init__(self, service_name: str = None):
        self.service_name = service_name or self.__class__.__name__
        self.logger = logger_service
        self._dependencies: Dict[str, Any] = {}
        
        # Log service initialization
        self.logger.info(f"Initializing service: {self.service_name}")
    
    def inject_dependency(self, name: str, dependency: Any):
        """Inject a dependency into the service"""
        self._dependencies[name] = dependency
        self.logger.trace(f"Injected dependency: {name} into {self.service_name}")
    
    def get_dependency(self, name: str, default: Any = None) -> Any:
        """Get an injected dependency"""
        return self._dependencies.get(name, default)
    
    def has_dependency(self, name: str) -> bool:
        """Check if a dependency is available"""
        return name in self._dependencies
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service (must be implemented by subclasses)"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup resources (can be overridden by subclasses)"""
        self.logger.info(f"Cleaning up service: {self.service_name}")

class ServiceRegistry:
    """
    Service registry for dependency injection and service management
    """
    
    _instance = None
    _services: Dict[str, BaseService] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_service(self, service: BaseService, name: str = None):
        """Register a service in the registry"""
        service_name = name or service.service_name
        self._services[service_name] = service
        logger_service.info(f"Registered service: {service_name}")
    
    def get_service(self, name: str, service_type: Type[T] = None) -> Optional[T]:
        """Get a service from the registry"""
        service = self._services.get(name)
        if service_type and service and not isinstance(service, service_type):
            logger_service.warning(f"Service {name} is not of expected type {service_type}")
            return None
        return service
    
    def remove_service(self, name: str):
        """Remove a service from the registry"""
        if name in self._services:
            service = self._services.pop(name)
            service.cleanup()
            logger_service.info(f"Removed service: {name}")
    
    def initialize_all(self):
        """Initialize all registered services"""
        for name, service in self._services.items():
            try:
                service.initialize()
                logger_service.info(f"Successfully initialized service: {name}")
            except Exception as e:
                logger_service.error(f"Failed to initialize service {name}: {str(e)}")
    
    def cleanup_all(self):
        """Cleanup all registered services"""
        for name, service in self._services.items():
            try:
                service.cleanup()
                logger_service.info(f"Successfully cleaned up service: {name}")
            except Exception as e:
                logger_service.error(f"Failed to cleanup service {name}: {str(e)}")

# Global service registry instance
service_registry = ServiceRegistry() 