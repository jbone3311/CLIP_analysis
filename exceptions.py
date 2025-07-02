"""
Custom exception classes for the image analysis project.

Provides a comprehensive error hierarchy with proper error handling,
logging, and user-friendly error messages.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ImageAnalysisError(Exception):
    """Base exception for all image analysis errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize base exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code  
            details: Additional error details (will be logged but not exposed)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        
        # Log the error with full details
        logger.error(
            f"{self.error_code}: {message}",
            extra={
                "error_code": self.error_code,
                "error_details": self.details,
                "exception_type": self.__class__.__name__
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "type": self.__class__.__name__
        }

class ConfigurationError(ImageAnalysisError):
    """Raised when there are configuration issues."""
    pass

class ValidationError(ImageAnalysisError):
    """Raised when input validation fails."""
    pass

class ImageValidationError(ValidationError):
    """Raised when image file validation fails."""
    pass

class PathValidationError(ValidationError):
    """Raised when file path validation fails."""
    pass

class APIError(ImageAnalysisError):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_data: Optional[Dict] = None, **kwargs):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_data: API response data (will be sanitized)
        """
        self.status_code = status_code
        self.response_data = self._sanitize_response_data(response_data)
        
        details = kwargs.get('details', {})
        details.update({
            "status_code": status_code,
            "response_data": self.response_data
        })
        
        super().__init__(message, **kwargs, details=details)
    
    def _sanitize_response_data(self, data: Optional[Dict]) -> Optional[Dict]:
        """Sanitize response data to remove sensitive information."""
        if not data:
            return None
        
        # Remove potentially sensitive fields
        sensitive_fields = ['api_key', 'token', 'authorization', 'password', 'secret']
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_response_data(value)
            else:
                sanitized[key] = value
        
        return sanitized

class LLMAPIError(APIError):
    """Raised when LLM API calls fail."""
    pass

class CLIPAPIError(APIError):
    """Raised when CLIP API calls fail."""
    pass

class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        details = kwargs.get('details', {})
        details['retry_after'] = retry_after
        
        super().__init__(message, **kwargs, details=details)

class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass

class NetworkError(ImageAnalysisError):
    """Raised when network operations fail."""
    pass

class DatabaseError(ImageAnalysisError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        """
        Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
        """
        self.operation = operation
        details = kwargs.get('details', {})
        details['operation'] = operation
        
        super().__init__(message, **kwargs, details=details)

class FileOperationError(ImageAnalysisError):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 operation: Optional[str] = None, **kwargs):
        """
        Initialize file operation error.
        
        Args:
            message: Error message
            file_path: Path to file that caused error
            operation: File operation that failed
        """
        self.file_path = file_path
        self.operation = operation
        
        details = kwargs.get('details', {})
        details.update({
            'file_path': file_path,
            'operation': operation
        })
        
        super().__init__(message, **kwargs, details=details)

class ProcessingError(ImageAnalysisError):
    """Raised when image processing fails."""
    
    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        """
        Initialize processing error.
        
        Args:
            message: Error message
            stage: Processing stage where error occurred
        """
        self.stage = stage
        details = kwargs.get('details', {})
        details['stage'] = stage
        
        super().__init__(message, **kwargs, details=details)

class TimeoutError(ImageAnalysisError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Timeout value that was exceeded
        """
        self.timeout_seconds = timeout_seconds
        details = kwargs.get('details', {})
        details['timeout_seconds'] = timeout_seconds
        
        super().__init__(message, **kwargs, details=details)

class ResourceError(ImageAnalysisError):
    """Raised when system resources are exhausted."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        """
        Initialize resource error.
        
        Args:
            message: Error message
            resource_type: Type of resource that was exhausted
        """
        self.resource_type = resource_type
        details = kwargs.get('details', {})
        details['resource_type'] = resource_type
        
        super().__init__(message, **kwargs, details=details)

def handle_api_error(response, operation: str = "API call") -> None:
    """
    Handle API response and raise appropriate exception.
    
    Args:
        response: HTTP response object
        operation: Description of the operation that failed
        
    Raises:
        APIError: Appropriate API error based on status code
    """
    try:
        response_data = response.json() if response.content else {}
    except ValueError:
        response_data = {"raw_content": response.text[:500]}  # Limit size
    
    status_code = response.status_code
    
    if status_code == 401:
        raise AuthenticationError(
            f"Authentication failed for {operation}",
            status_code=status_code,
            response_data=response_data
        )
    elif status_code == 429:
        retry_after = response.headers.get('Retry-After')
        retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
        
        raise RateLimitError(
            f"Rate limit exceeded for {operation}",
            status_code=status_code,
            retry_after=retry_after_int,
            response_data=response_data
        )
    elif 400 <= status_code < 500:
        raise APIError(
            f"Client error in {operation}: {response_data.get('error', 'Unknown error')}",
            status_code=status_code,
            response_data=response_data
        )
    elif 500 <= status_code < 600:
        raise APIError(
            f"Server error in {operation}: {response_data.get('error', 'Internal server error')}",
            status_code=status_code,
            response_data=response_data
        )
    else:
        raise APIError(
            f"Unexpected status code {status_code} for {operation}",
            status_code=status_code,
            response_data=response_data
        )

def safe_error_message(error: Exception) -> str:
    """
    Generate a safe, user-friendly error message.
    
    Args:
        error: Exception to convert
        
    Returns:
        Safe error message without sensitive information
    """
    if isinstance(error, ImageAnalysisError):
        return error.message
    elif isinstance(error, FileNotFoundError):
        return "File not found. Please check the file path and try again."
    elif isinstance(error, PermissionError):
        return "Permission denied. Please check file permissions."
    elif isinstance(error, OSError):
        return "System error occurred. Please try again or contact support."
    else:
        # For unknown exceptions, provide generic message
        logger.error(f"Unhandled exception: {type(error).__name__}: {str(error)}")
        return "An unexpected error occurred. Please try again or contact support."

def log_error_context(error: Exception, context: Dict[str, Any]) -> None:
    """
    Log error with additional context for debugging.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        extra={
            "exception_type": type(error).__name__,
            "exception_message": str(error),
            "context": context
        },
        exc_info=True
    )