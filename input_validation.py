"""
Input validation module for image analysis project.

Provides comprehensive validation for image files, paths, and user inputs
to prevent security vulnerabilities and resource exhaustion.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Configuration constants
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PATH_LENGTH = 260  # Windows MAX_PATH limitation
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/bmp': ['.bmp'],
    'image/webp': ['.webp']
}

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class ImageValidationError(ValidationError):
    """Raised when image validation fails."""
    pass

class PathValidationError(ValidationError):
    """Raised when path validation fails."""
    pass

def validate_file_path(file_path: str) -> Path:
    """
    Validate file path for security and existence.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validated Path object
        
    Raises:
        PathValidationError: If path is invalid or unsafe
    """
    if not file_path or not isinstance(file_path, str):
        raise PathValidationError("File path must be a non-empty string")
    
    # Check path length
    if len(file_path) > MAX_PATH_LENGTH:
        raise PathValidationError(f"File path too long (max {MAX_PATH_LENGTH} characters)")
    
    # Convert to Path object for safer handling
    try:
        path = Path(file_path).resolve()
    except (OSError, ValueError) as e:
        raise PathValidationError(f"Invalid file path: {e}")
    
    # Check for path traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        logger.warning(f"Potential path traversal attempt: {file_path}")
        raise PathValidationError("Path traversal attempts are not allowed")
    
    # Check if file exists
    if not path.exists():
        raise PathValidationError(f"File does not exist: {file_path}")
    
    # Check if it's actually a file
    if not path.is_file():
        raise PathValidationError(f"Path is not a file: {file_path}")
    
    return path

def validate_file_size(file_path: Path) -> int:
    """
    Validate file size to prevent memory exhaustion.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
        
    Raises:
        ImageValidationError: If file is too large
    """
    try:
        file_size = file_path.stat().st_size
    except OSError as e:
        raise ImageValidationError(f"Cannot read file size: {e}")
    
    if file_size == 0:
        raise ImageValidationError("File is empty")
    
    if file_size > MAX_FILE_SIZE:
        raise ImageValidationError(
            f"File too large: {file_size / 1024 / 1024:.1f}MB "
            f"(max {MAX_FILE_SIZE / 1024 / 1024}MB)"
        )
    
    return file_size

def validate_image_format(file_path: Path) -> str:
    """
    Validate image format using MIME type detection.
    
    Args:
        file_path: Path to image file
        
    Returns:
        MIME type of the image
        
    Raises:
        ImageValidationError: If format is not supported
    """
    # Check file extension
    extension = file_path.suffix.lower()
    
    # Get MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if not mime_type or not mime_type.startswith('image/'):
        raise ImageValidationError(f"Not an image file: {mime_type}")
    
    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise ImageValidationError(
            f"Unsupported image format: {mime_type}. "
            f"Supported formats: {list(ALLOWED_IMAGE_TYPES.keys())}"
        )
    
    # Verify extension matches MIME type
    expected_extensions = ALLOWED_IMAGE_TYPES[mime_type]
    if extension not in expected_extensions:
        logger.warning(
            f"Extension mismatch: file has {extension} but MIME type is {mime_type}"
        )
    
    return mime_type

def validate_image_content(file_path: Path) -> bool:
    """
    Basic validation of image file content.
    
    Args:
        file_path: Path to image file
        
    Returns:
        True if content appears valid
        
    Raises:
        ImageValidationError: If content is suspicious
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first few bytes to check magic numbers
            header = f.read(32)
        
        if not header:
            raise ImageValidationError("File appears to be empty")
        
        # Check for common image file signatures
        image_signatures = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'GIF87a': 'GIF87a',
            b'GIF89a': 'GIF89a',
            b'BM': 'BMP',
            b'RIFF': 'WebP/RIFF'
        }
        
        signature_found = False
        for signature, format_name in image_signatures.items():
            if header.startswith(signature):
                signature_found = True
                logger.debug(f"Detected {format_name} signature")
                break
        
        if not signature_found:
            logger.warning(f"No recognized image signature found in {file_path}")
        
        return True
        
    except OSError as e:
        raise ImageValidationError(f"Cannot read file content: {e}")

def validate_image_file(file_path: str) -> Tuple[Path, int, str]:
    """
    Comprehensive validation of image file.
    
    Args:
        file_path: Path to image file to validate
        
    Returns:
        Tuple of (validated_path, file_size, mime_type)
        
    Raises:
        ValidationError: If any validation step fails
    """
    logger.info(f"Validating image file: {file_path}")
    
    # Step 1: Validate path
    validated_path = validate_file_path(file_path)
    
    # Step 2: Validate file size
    file_size = validate_file_size(validated_path)
    
    # Step 3: Validate image format
    mime_type = validate_image_format(validated_path)
    
    # Step 4: Basic content validation
    validate_image_content(validated_path)
    
    logger.info(
        f"Image validation successful: {file_path} "
        f"({file_size / 1024:.1f}KB, {mime_type})"
    )
    
    return validated_path, file_size, mime_type

def validate_prompt_input(prompt: str) -> str:
    """
    Validate prompt input for security and length.
    
    Args:
        prompt: Prompt string to validate
        
    Returns:
        Cleaned prompt string
        
    Raises:
        ValidationError: If prompt is invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValidationError("Prompt must be a non-empty string")
    
    # Remove potential injection attempts
    cleaned_prompt = prompt.strip()
    
    # Check length
    if len(cleaned_prompt) > 10000:  # Reasonable limit
        raise ValidationError("Prompt too long (max 10,000 characters)")
    
    # Check for suspicious patterns
    suspicious_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    for pattern in suspicious_patterns:
        if pattern.lower() in cleaned_prompt.lower():
            logger.warning(f"Suspicious pattern detected in prompt: {pattern}")
            raise ValidationError("Prompt contains suspicious content")
    
    return cleaned_prompt

def validate_output_path(output_path: str) -> Path:
    """
    Validate output file path for writing.
    
    Args:
        output_path: Path where output will be written
        
    Returns:
        Validated Path object
        
    Raises:
        PathValidationError: If path is invalid for writing
    """
    if not output_path or not isinstance(output_path, str):
        raise PathValidationError("Output path must be a non-empty string")
    
    try:
        path = Path(output_path).resolve()
    except (OSError, ValueError) as e:
        raise PathValidationError(f"Invalid output path: {e}")
    
    # Check if parent directory exists
    parent_dir = path.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise PathValidationError(f"Cannot create output directory: {e}")
    
    # Check if we can write to the directory
    if not os.access(parent_dir, os.W_OK):
        raise PathValidationError(f"No write permission for directory: {parent_dir}")
    
    return path

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    # Replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    sanitized = filename
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty after sanitization
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized

def validate_api_response(response_data: dict) -> dict:
    """
    Validate API response structure and content.
    
    Args:
        response_data: Response data from API
        
    Returns:
        Validated response data
        
    Raises:
        ValidationError: If response is invalid
    """
    if not isinstance(response_data, dict):
        raise ValidationError("API response must be a dictionary")
    
    # Check for common error indicators
    if 'error' in response_data:
        error_msg = response_data.get('error', 'Unknown error')
        raise ValidationError(f"API returned error: {error_msg}")
    
    # Additional validation can be added based on specific API contracts
    
    return response_data