#!/usr/bin/env python3
"""
Centralized Logging Utility

Provides consistent logging across the entire application with:
- Configurable log levels
- Structured logging with context
- Performance monitoring
- Error tracking
- Debug utilities
"""

import os
import sys
import logging
import logging.handlers
import time
import traceback
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    try:
        import codecs
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except Exception:
        pass  # Ignore encoding errors


class PerformanceTracker:
    """Tracks performance metrics for operations"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            del self.start_times[operation]
            return duration
        return 0.0
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation"""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        durations = self.metrics[operation]
        return {
            'count': len(durations),
            'total': sum(durations),
            'average': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'latest': durations[-1]
        }


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record):
        # Add structured data if available
        if hasattr(record, 'structured_data'):
            record.structured_data_str = json.dumps(record.structured_data, default=str)
        else:
            record.structured_data_str = ''
        
        # Add performance data if available
        if hasattr(record, 'performance_data'):
            record.performance_str = f" | {record.performance_data}"
        else:
            record.performance_str = ''
        
        return super().format(record)


class AppLogger:
    """Centralized application logger with advanced features"""
    
    def __init__(self, name: str = 'clip_analysis', config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.performance_tracker = PerformanceTracker()
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup the logger with proper configuration"""
        logger = logging.getLogger(self.name)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Set log level
        log_level = self.config.get('log_level', 'INFO').upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Create formatters
        console_formatter = StructuredFormatter(
            '[%(asctime)s] %(levelname)s: %(name)s - %(message)s%(performance_str)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_formatter = StructuredFormatter(
            '[%(asctime)s] %(levelname)s: %(name)s - %(message)s | %(structured_data_str)s%(performance_str)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.config.get('log_file', 'app.log')
        max_size = self.config.get('max_size', 10 * 1024 * 1024)  # 10MB
        backup_count = self.config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_size, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = self.config.get('error_log_file', 'errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with additional context"""
        extra = {}
        
        # Add structured data
        if 'data' in kwargs:
            extra['structured_data'] = kwargs['data']
        
        # Add performance data
        if 'operation' in kwargs:
            duration = self.performance_tracker.end(kwargs['operation'])
            if duration > 0:
                extra['performance_data'] = f"Duration: {duration:.3f}s"
        
        # Add context
        if 'context' in kwargs:
            extra['context'] = kwargs['context']
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        kwargs['data'] = {
            'traceback': traceback.format_exc(),
            **kwargs.get('data', {})
        }
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message with optional exception info"""
        if exc_info:
            kwargs['data'] = {
                'traceback': traceback.format_exc(),
                **kwargs.get('data', {})
            }
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def performance(self, operation: str, message: str = None, **kwargs):
        """Log performance information"""
        stats = self.performance_tracker.get_stats(operation)
        if stats:
            kwargs['data'] = {**kwargs.get('data', {}), 'performance': stats}
            self.info(message or f"Performance stats for {operation}", **kwargs)
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.performance_tracker.start(operation)
        self.debug(f"Started timing operation: {operation}")
    
    def end_timer(self, operation: str, message: str = None):
        """End timing an operation and log the duration"""
        duration = self.performance_tracker.end(operation)
        if duration > 0:
            self.info(message or f"Completed operation: {operation}", 
                     operation=operation, data={'duration': duration})
        return duration
    
    @contextmanager
    def timed_operation(self, operation: str, message: str = None):
        """Context manager for timing operations"""
        self.start_timer(operation)
        try:
            yield
        finally:
            self.end_timer(operation, message)
    
    def log_function_call(self, func_name: str, args: tuple = None, kwargs: dict = None):
        """Log function call details"""
        call_data = {
            'function': func_name,
            'args': str(args) if args else None,
            'kwargs': kwargs
        }
        self.debug(f"Function call: {func_name}", data=call_data)
    
    def log_api_request(self, method: str, url: str, status_code: int = None, 
                       duration: float = None, error: str = None):
        """Log API request details"""
        request_data = {
            'method': method,
            'url': url,
            'status_code': status_code,
            'duration': duration,
            'error': error
        }
        
        if error:
            self.error(f"API request failed: {method} {url}", data=request_data)
        else:
            self.info(f"API request: {method} {url} - {status_code}", data=request_data)


def get_logger(name: str = None, config: Dict[str, Any] = None) -> AppLogger:
    """Get a logger instance"""
    if name is None:
        name = 'clip_analysis'
    
    # Load config from environment if not provided
    if config is None:
        config = {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'app.log'),
            'error_log_file': os.getenv('ERROR_LOG_FILE', 'errors.log'),
            'max_size': int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024)),
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', 5))
        }
    
    return AppLogger(name, config)


def log_function_calls(logger: AppLogger = None):
    """Decorator to log function calls"""
    if logger is None:
        logger = get_logger()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log_function_call(func.__name__, args, kwargs)
            logger.start_timer(f"{func.__module__}.{func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.end_timer(f"{func.__module__}.{func.__name__}")
                return result
            except Exception as e:
                logger.exception(f"Function {func.__name__} failed", 
                               data={'function': func.__name__, 'error': str(e)})
                raise
        
        return wrapper
    return decorator


def log_api_calls(logger: AppLogger = None):
    """Decorator to log API calls"""
    if logger is None:
        logger = get_logger()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to extract request info from result
                status_code = getattr(result, 'status_code', None)
                logger.log_api_request('POST', 'API', status_code, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_api_request('POST', 'API', error=str(e), duration=duration)
                raise
        
        return wrapper
    return decorator


# Global logger instance
_global_logger = None

def get_global_logger() -> AppLogger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = get_logger()
    return _global_logger


def setup_global_logging(config: Dict[str, Any] = None):
    """Setup global logging configuration"""
    global _global_logger
    _global_logger = get_logger(config=config)
    return _global_logger 