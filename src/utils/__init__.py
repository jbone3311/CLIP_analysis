"""
Utilities Package

This package contains utility functions and helper scripts.
"""

from .file_utils import (
    compute_file_hash,
    ensure_directory_exists,
    get_file_size,
    is_valid_image_file,
    find_image_files,
    normalize_path,
    get_relative_path
)
from .progress import ProgressTracker, ProgressState
from .logger import get_global_logger, setup_global_logging
from .error_handler import ErrorCategory, error_context, handle_errors
from .installer import main as install_system

__all__ = [
    # File utilities
    'compute_file_hash',
    'ensure_directory_exists',
    'get_file_size',
    'is_valid_image_file',
    'find_image_files',
    'normalize_path',
    'get_relative_path',
    # Progress tracking
    'ProgressTracker',
    'ProgressState',
    # Logging
    'get_global_logger',
    'setup_global_logging',
    # Error handling
    'ErrorCategory',
    'error_context',
    'handle_errors',
    # Installer
    'install_system',
] 