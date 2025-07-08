#!/usr/bin/env python3
"""
Error Handling Utility

Provides comprehensive error handling with:
- Detailed error context
- Recovery strategies
- Error categorization
- Debugging information
- Graceful degradation
"""

import os
import sys
import traceback
import time
from typing import Dict, Any, Optional, Callable, Type, Union
from functools import wraps
from contextlib import contextmanager
from enum import Enum

from .logger import get_logger, AppLogger


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    FILE_IO = "file_io"
    API = "api"
    DATABASE = "database"
    VALIDATION = "validation"
    PERMISSION = "permission"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorContext:
    """Provides context for error handling"""
    
    def __init__(self, operation: str, category: ErrorCategory = ErrorCategory.UNKNOWN):
        self.operation = operation
        self.category = category
        self.start_time = time.time()
        self.retry_count = 0
        self.max_retries = 3
        self.context_data = {}
    
    def add_context(self, key: str, value: Any):
        """Add context data"""
        self.context_data[key] = value
    
    def get_duration(self) -> float:
        """Get operation duration"""
        return time.time() - self.start_time


class ErrorHandler:
    """Main error handling class"""
    
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or get_logger()
        self.error_counts = {}
        self.recovery_strategies = {}
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        # Network errors - retry with exponential backoff
        self.recovery_strategies[ErrorCategory.NETWORK] = {
            'max_retries': 3,
            'backoff_factor': 2,
            'base_delay': 1.0,
            'retryable_exceptions': [
                'ConnectionError',
                'TimeoutError',
                'requests.exceptions.RequestException'
            ]
        }
        
        # File I/O errors - retry with short delay
        self.recovery_strategies[ErrorCategory.FILE_IO] = {
            'max_retries': 2,
            'backoff_factor': 1.5,
            'base_delay': 0.5,
            'retryable_exceptions': [
                'PermissionError',
                'FileNotFoundError',
                'OSError'
            ]
        }
        
        # API errors - retry with exponential backoff
        self.recovery_strategies[ErrorCategory.API] = {
            'max_retries': 3,
            'backoff_factor': 2,
            'base_delay': 1.0,
            'retryable_exceptions': [
                'requests.exceptions.HTTPError',
                'requests.exceptions.Timeout',
                'requests.exceptions.ConnectionError'
            ]
        }
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize an error based on its type"""
        error_type = type(error).__name__
        error_str = str(error).lower()
        
        # Network errors
        if any(network_term in error_str for network_term in ['connection', 'timeout', 'network', 'dns']):
            return ErrorCategory.NETWORK
        
        # File I/O errors
        if any(file_term in error_str for file_term in ['file', 'directory', 'path', 'permission']):
            return ErrorCategory.FILE_IO
        
        # API errors
        if any(api_term in error_str for api_term in ['api', 'http', 'request', 'response']):
            return ErrorCategory.API
        
        # Database errors
        if any(db_term in error_str for db_term in ['database', 'sql', 'db']):
            return ErrorCategory.DATABASE
        
        # Configuration errors
        if any(config_term in error_str for config_term in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        
        # Validation errors
        if any(validation_term in error_str for validation_term in ['validation', 'invalid', 'format']):
            return ErrorCategory.VALIDATION
        
        # Permission errors
        if any(permission_term in error_str for permission_term in ['permission', 'access', 'denied']):
            return ErrorCategory.PERMISSION
        
        # Resource errors
        if any(resource_term in error_str for resource_term in ['memory', 'disk', 'resource']):
            return ErrorCategory.RESOURCE
        
        return ErrorCategory.UNKNOWN
    
    def get_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """Determine error severity"""
        error_type = type(error).__name__
        
        # Critical errors
        if error_type in ['KeyboardInterrupt', 'SystemExit']:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if error_type in ['MemoryError', 'OSError'] or context.category in [ErrorCategory.DATABASE]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if context.category in [ErrorCategory.NETWORK, ErrorCategory.API]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        if context.category in [ErrorCategory.VALIDATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def should_retry(self, error: Exception, context: ErrorContext) -> bool:
        """Determine if an error should be retried"""
        if context.retry_count >= context.max_retries:
            return False
        
        strategy = self.recovery_strategies.get(context.category)
        if not strategy:
            return False
        
        error_type = type(error).__name__
        return error_type in strategy.get('retryable_exceptions', [])
    
    def get_retry_delay(self, context: ErrorContext) -> float:
        """Calculate retry delay with exponential backoff"""
        strategy = self.recovery_strategies.get(context.category, {})
        base_delay = strategy.get('base_delay', 1.0)
        backoff_factor = strategy.get('backoff_factor', 2.0)
        
        return base_delay * (backoff_factor ** context.retry_count)
    
    def handle_error(self, error: Exception, context: ErrorContext, 
                    operation: str = None) -> Dict[str, Any]:
        """Handle an error with full context"""
        # Update context
        if operation:
            context.operation = operation
        
        # Categorize and assess severity
        context.category = self.categorize_error(error)
        severity = self.get_severity(error, context)
        
        # Update error counts
        error_key = f"{context.category.value}_{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Prepare error data
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': context.category.value,
            'severity': severity.value,
            'operation': context.operation,
            'duration': context.get_duration(),
            'retry_count': context.retry_count,
            'context_data': context.context_data,
            'traceback': traceback.format_exc(),
            'error_count': self.error_counts[error_key]
        }
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error in {context.operation}", data=error_data)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error in {context.operation}", data=error_data)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error in {context.operation}", data=error_data)
        else:
            self.logger.info(f"Low severity error in {context.operation}", data=error_data)
        
        return error_data
    
    def retry_operation(self, operation: Callable, context: ErrorContext, 
                       *args, **kwargs) -> Any:
        """Retry an operation with error handling"""
        while True:
            try:
                return operation(*args, **kwargs)
            except Exception as error:
                error_data = self.handle_error(error, context)
                
                if not self.should_retry(error, context):
                    raise error
                
                context.retry_count += 1
                delay = self.get_retry_delay(context)
                
                self.logger.info(f"Retrying {context.operation} in {delay:.2f}s (attempt {context.retry_count})")
                time.sleep(delay)
    
    def safe_execute(self, operation: Callable, context: ErrorContext, 
                    fallback: Callable = None, *args, **kwargs) -> Any:
        """Safely execute an operation with fallback"""
        try:
            return operation(*args, **kwargs)
        except Exception as error:
            error_data = self.handle_error(error, context)
            
            if fallback:
                self.logger.info(f"Using fallback for {context.operation}")
                try:
                    return fallback(*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed for {context.operation}", 
                                    data={'fallback_error': str(fallback_error)})
            
            raise error


def handle_errors(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 max_retries: int = 3, fallback: Callable = None):
    """Decorator for error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = ErrorContext(func.__name__, category)
            context.max_retries = max_retries
            
            handler = ErrorHandler()
            
            if fallback:
                return handler.safe_execute(func, context, fallback, *args, **kwargs)
            else:
                return handler.retry_operation(func, context, *args, **kwargs)
        
        return wrapper
    return decorator


@contextmanager
def error_context(operation: str, category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Context manager for error handling"""
    context = ErrorContext(operation, category)
    handler = ErrorHandler()
    
    try:
        yield context
    except Exception as error:
        handler.handle_error(error, context)
        raise


def graceful_degradation(default_value: Any = None):
    """Decorator for graceful degradation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                logger = get_logger()
                logger.warning(f"Function {func.__name__} failed, using default value", 
                             data={'error': str(error), 'default_value': default_value})
                return default_value
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler = None

def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def setup_global_error_handling(logger: AppLogger = None):
    """Setup global error handling"""
    global _global_error_handler
    _global_error_handler = ErrorHandler(logger)
    return _global_error_handler 