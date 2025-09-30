#!/usr/bin/env python3
"""
Debugging Utilities

Provides comprehensive debugging capabilities:
- Variable inspection and pretty printing
- Performance profiling
- Memory usage tracking
- Debug decorators
- Interactive debugging helpers
"""

import os
import sys
import time
import inspect
import traceback
import psutil
import gc
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from contextlib import contextmanager
import json
from datetime import datetime

from .logger import get_logger, AppLogger


class DebugInspector:
    """Inspects and displays debug information"""
    
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or get_logger()
    
    def inspect_variable(self, var: Any, name: str = "variable", max_depth: int = 3) -> Dict[str, Any]:
        """Inspect a variable and return detailed information"""
        info = {
            'name': name,
            'type': type(var).__name__,
            'id': id(var),
            'size': self._get_size(var),
            'repr': repr(var)[:200] + "..." if len(repr(var)) > 200 else repr(var)
        }
        
        if max_depth > 0:
            info['attributes'] = self._get_attributes(var, max_depth - 1)
        
        return info
    
    def _get_size(self, obj: Any) -> int:
        """Get approximate size of an object"""
        try:
            return sys.getsizeof(obj)
        except:
            return 0
    
    def _get_attributes(self, obj: Any, max_depth: int) -> Dict[str, Any]:
        """Get object attributes recursively"""
        if max_depth <= 0:
            return {}
        
        attrs = {}
        try:
            for attr_name in dir(obj):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(obj, attr_name)
                        if not callable(attr_value):
                            attrs[attr_name] = {
                                'type': type(attr_value).__name__,
                                'value': str(attr_value)[:100] + "..." if len(str(attr_value)) > 100 else str(attr_value)
                            }
                    except Exception:
                        attrs[attr_name] = {'type': 'error', 'value': 'Could not access'}
        except Exception:
            pass
        
        return attrs
    
    def print_variable(self, var: Any, name: str = "variable", max_depth: int = 3):
        """Print variable information"""
        info = self.inspect_variable(var, name, max_depth)
        self.logger.debug(f"Variable inspection: {name}", data=info)
    
    def inspect_function(self, func: Callable) -> Dict[str, Any]:
        """Inspect a function and return detailed information"""
        try:
            sig = inspect.signature(func)
            info = {
                'name': func.__name__,
                'module': func.__module__,
                'doc': func.__doc__,
                'parameters': list(sig.parameters.keys()),
                'return_annotation': str(sig.return_annotation),
                'source': inspect.getsource(func)[:500] + "..." if len(inspect.getsource(func)) > 500 else inspect.getsource(func)
            }
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def print_function(self, func: Callable):
        """Print function information"""
        info = self.inspect_function(func)
        self.logger.debug(f"Function inspection: {func.__name__}", data=info)


class PerformanceProfiler:
    """Profiles performance of operations"""
    
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or get_logger()
        self.profiles = {}
        self.active_profiles = {}
    
    def start_profile(self, name: str):
        """Start profiling an operation"""
        self.active_profiles[name] = {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'start_cpu': psutil.Process().cpu_percent()
        }
        self.logger.debug(f"Started profiling: {name}")
    
    def end_profile(self, name: str) -> Dict[str, Any]:
        """End profiling and return results"""
        if name not in self.active_profiles:
            return {}
        
        start_data = self.active_profiles[name]
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        end_cpu = psutil.Process().cpu_percent()
        
        profile_data = {
            'duration': end_time - start_data['start_time'],
            'memory_delta': end_memory - start_data['start_memory'],
            'memory_usage': end_memory,
            'cpu_usage': end_cpu,
            'timestamp': datetime.now().isoformat()
        }
        
        if name not in self.profiles:
            self.profiles[name] = []
        
        self.profiles[name].append(profile_data)
        del self.active_profiles[name]
        
        self.logger.info(f"Profile completed: {name}", data=profile_data)
        return profile_data
    
    def get_profile_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a profile"""
        if name not in self.profiles or not self.profiles[name]:
            return {}
        
        durations = [p['duration'] for p in self.profiles[name]]
        memory_deltas = [p['memory_delta'] for p in self.profiles[name]]
        
        return {
            'count': len(durations),
            'total_duration': sum(durations),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_memory_delta': sum(memory_deltas),
            'avg_memory_delta': sum(memory_deltas) / len(memory_deltas)
        }
    
    @contextmanager
    def profile(self, name: str):
        """Context manager for profiling"""
        self.start_profile(name)
        try:
            yield
        finally:
            self.end_profile(name)


class MemoryTracker:
    """Tracks memory usage"""
    
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or get_logger()
        self.snapshots = []
    
    def take_snapshot(self, label: str = None):
        """Take a memory snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = {
            'label': label or f"snapshot_{len(self.snapshots)}",
            'timestamp': datetime.now().isoformat(),
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent()
        }
        
        self.snapshots.append(snapshot)
        self.logger.debug(f"Memory snapshot: {snapshot['label']}", data=snapshot)
        return snapshot
    
    def compare_snapshots(self, label1: str, label2: str) -> Dict[str, Any]:
        """Compare two memory snapshots"""
        snap1 = next((s for s in self.snapshots if s['label'] == label1), None)
        snap2 = next((s for s in self.snapshots if s['label'] == label2), None)
        
        if not snap1 or not snap2:
            return {}
        
        return {
            'rss_delta': snap2['rss'] - snap1['rss'],
            'vms_delta': snap2['vms'] - snap1['vms'],
            'percent_delta': snap2['percent'] - snap1['percent'],
            'time_delta': (datetime.fromisoformat(snap2['timestamp']) - 
                          datetime.fromisoformat(snap1['timestamp'])).total_seconds()
        }
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get current memory summary"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent(),
            'snapshots_count': len(self.snapshots)
        }


def debug_function(logger: AppLogger = None, profile: bool = True, inspect_args: bool = True):
    """Decorator to debug function calls"""
    if logger is None:
        logger = get_logger()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log function call
            logger.debug(f"Function call: {func.__name__}", 
                        data={'args_count': len(args), 'kwargs_count': len(kwargs)})
            
            # Inspect arguments if requested
            if inspect_args:
                inspector = DebugInspector(logger)
                for i, arg in enumerate(args):
                    inspector.print_variable(arg, f"arg_{i}")
                for key, value in kwargs.items():
                    inspector.print_variable(value, f"kwarg_{key}")
            
            # Profile if requested
            if profile:
                profiler = PerformanceProfiler(logger)
                with profiler.profile(f"{func.__module__}.{func.__name__}"):
                    try:
                        result = func(*args, **kwargs)
                        logger.debug(f"Function completed: {func.__name__}")
                        return result
                    except Exception as e:
                        logger.exception(f"Function failed: {func.__name__}", 
                                       data={'error': str(e)})
                        raise
            else:
                try:
                    result = func(*args, **kwargs)
                    logger.debug(f"Function completed: {func.__name__}")
                    return result
                except Exception as e:
                    logger.exception(f"Function failed: {func.__name__}", 
                                   data={'error': str(e)})
                    raise
        
        return wrapper
    return decorator


def debug_class_methods(logger: AppLogger = None):
    """Decorator to debug all methods in a class"""
    if logger is None:
        logger = get_logger()
    
    def decorator(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, debug_function(logger)(attr))
        return cls
    return decorator


@contextmanager
def debug_context(label: str, logger: AppLogger = None):
    """Context manager for debugging"""
    if logger is None:
        logger = get_logger()
    
    logger.debug(f"Entering debug context: {label}")
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    try:
        yield
    except Exception as e:
        logger.exception(f"Error in debug context: {label}", data={'error': str(e)})
        raise
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        duration = end_time - start_time
        memory_delta = end_memory - start_memory
        
        logger.debug(f"Exiting debug context: {label}", 
                    data={'duration': duration, 'memory_delta': memory_delta})


def enable_debug_mode():
    """Enable debug mode globally"""
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['DEBUG'] = 'True'
    
    logger = get_logger()
    logger.info("Debug mode enabled")


def disable_debug_mode():
    """Disable debug mode globally"""
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['DEBUG'] = 'False'
    
    logger = get_logger()
    logger.info("Debug mode disabled")


def get_debug_info() -> Dict[str, Any]:
    """Get comprehensive debug information"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'system': {
            'platform': sys.platform,
            'python_version': sys.version,
            'executable': sys.executable
        },
        'process': {
            'pid': process.pid,
            'name': process.name(),
            'memory_rss_mb': memory_info.rss / 1024 / 1024,
            'memory_vms_mb': memory_info.vms / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent()
        },
        'environment': {
            'debug_enabled': os.getenv('DEBUG', 'False') == 'True',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'working_directory': os.getcwd()
        },
        'gc': {
            'garbage_count': len(gc.garbage),
            'collection_counts': gc.get_count()
        }
    }


# Global instances
_global_inspector = None
_global_profiler = None
_global_memory_tracker = None

def get_global_inspector() -> DebugInspector:
    """Get global debug inspector"""
    global _global_inspector
    if _global_inspector is None:
        _global_inspector = DebugInspector()
    return _global_inspector

def get_global_profiler() -> PerformanceProfiler:
    """Get global performance profiler"""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler

def get_global_memory_tracker() -> MemoryTracker:
    """Get global memory tracker"""
    global _global_memory_tracker
    if _global_memory_tracker is None:
        _global_memory_tracker = MemoryTracker()
    return _global_memory_tracker


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