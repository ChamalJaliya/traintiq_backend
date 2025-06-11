"""
Professional Logging Service for TraintiQ Backend
Supports INFO, ERROR, WARNING, and TRACE levels with structured logging
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class LoggerService:
    """
    Professional logging service with multiple levels and structured output
    """
    
    def __init__(self, 
                 service_name: str = "TraintiQ", 
                 log_level: str = "INFO",
                 log_to_file: bool = True,
                 log_to_console: bool = True):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatters
        self.console_formatter = self._create_console_formatter()
        self.file_formatter = self._create_file_formatter()
        
        # Setup handlers
        if log_to_console:
            self._setup_console_handler()
        
        if log_to_file:
            self._setup_file_handlers()
    
    def _create_console_formatter(self) -> logging.Formatter:
        """Create colorized console formatter"""
        return ColorizedFormatter(
            fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _create_file_formatter(self) -> logging.Formatter:
        """Create structured file formatter"""
        return JsonFormatter()
    
    def _setup_console_handler(self):
        """Setup console handler with colors"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """Setup rotating file handlers"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # General log file (all levels)
        general_handler = RotatingFileHandler(
            log_dir / "traintiq.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(general_handler)
        
        # Error log file (errors only)
        error_handler = RotatingFileHandler(
            log_dir / "traintiq_errors.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(error_handler)
        
        # Daily rotating handler
        daily_handler = TimedRotatingFileHandler(
            log_dir / "traintiq_daily.log",
            when='midnight',
            interval=1,
            backupCount=30
        )
        daily_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(daily_handler)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info level message"""
        self._log(logging.INFO, message, extra, **kwargs)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning level message"""
        self._log(logging.WARNING, message, extra, **kwargs)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error level message"""
        self._log(logging.ERROR, message, extra, **kwargs)
    
    def trace(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log trace level message (using DEBUG level)"""
        self._log(logging.DEBUG, f"[TRACE] {message}", extra, **kwargs)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical level message"""
        self._log(logging.CRITICAL, message, extra, **kwargs)
    
    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal logging method with structured data"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'service': self.service_name,
            'message': message,
            **kwargs
        }
        
        if extra:
            log_data.update(extra)
        
        # Add context information
        import inspect
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back
            log_data.update({
                'function': caller_frame.f_code.co_name,
                'file': os.path.basename(caller_frame.f_code.co_filename),
                'line': caller_frame.f_lineno
            })
        finally:
            del frame
        
        # Create custom record with our data
        record = self.logger.makeRecord(
            self.logger.name, level, 
            log_data.get('file', 'unknown'), log_data.get('line', 0),
            message, (), None, log_data.get('function', 'unknown')
        )
        
        # Add our custom data
        for key, value in log_data.items():
            if key not in ['message', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'funcName', 'lineno']:
                setattr(record, key, value)
        
        self.logger.handle(record)

class ColorizedFormatter(logging.Formatter):
    """Formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Color the level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

# Global logger instance
logger_service = LoggerService()

# Convenience functions for easy usage
def info(message: str, **kwargs):
    """Log info message"""
    logger_service.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message"""
    logger_service.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log error message"""
    logger_service.error(message, **kwargs)

def trace(message: str, **kwargs):
    """Log trace message"""
    logger_service.trace(message, **kwargs)

def critical(message: str, **kwargs):
    """Log critical message"""
    logger_service.critical(message, **kwargs)

# Context manager for request logging
class RequestLogger:
    """Context manager for request-level logging"""
    
    def __init__(self, request_id: str, endpoint: str):
        self.request_id = request_id
        self.endpoint = endpoint
        self.start_time = datetime.now()
    
    def __enter__(self):
        info(f"Request started: {self.endpoint}", 
             request_id=self.request_id, 
             endpoint=self.endpoint)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            error(f"Request failed: {self.endpoint}", 
                  request_id=self.request_id,
                  endpoint=self.endpoint,
                  duration=duration,
                  exception=str(exc_val))
        else:
            info(f"Request completed: {self.endpoint}", 
                 request_id=self.request_id,
                 endpoint=self.endpoint,
                 duration=duration)