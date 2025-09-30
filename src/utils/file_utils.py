"""
File Utilities

Common file operations including hashing, path manipulation, and file validation.
"""

import os
import hashlib
from typing import Optional
from pathlib import Path


def compute_file_hash(file_path: str, algorithm: str = 'md5', chunk_size: int = 4096) -> str:
    """
    Compute hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256')
        chunk_size: Size of chunks to read (default 4096 bytes)
        
    Returns:
        Hexadecimal hash string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If algorithm is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get hash function
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }
    
    if algorithm not in hash_algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Use one of {list(hash_algorithms.keys())}")
    
    hash_obj = hash_algorithms[algorithm]()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        raise IOError(f"Failed to compute hash for {file_path}: {e}")


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
        
    Raises:
        OSError: If directory cannot be created
    """
    os.makedirs(directory, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """
    Get size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return os.path.getsize(file_path)


def is_valid_image_file(file_path: str, extensions: Optional[tuple] = None) -> bool:
    """
    Check if a file is a valid image based on extension.
    
    Args:
        file_path: Path to the file
        extensions: Tuple of valid extensions (default: common image formats)
        
    Returns:
        True if file has a valid image extension
    """
    if extensions is None:
        extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
    
    return file_path.lower().endswith(extensions)


def find_image_files(directory: str, extensions: Optional[tuple] = None, recursive: bool = True) -> list[str]:
    """
    Find all image files in a directory.
    
    Args:
        directory: Directory to search
        extensions: Tuple of valid extensions
        recursive: If True, search subdirectories
        
    Returns:
        List of image file paths
        
    Raises:
        NotADirectoryError: If directory doesn't exist
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    if extensions is None:
        extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
    
    image_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    full_path = os.path.join(root, file)
                    image_files.append(full_path)
    else:
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path) and file.lower().endswith(extensions):
                image_files.append(full_path)
    
    return sorted(image_files)


def normalize_path(path: str) -> str:
    """
    Normalize a file path (expand user, resolve relative paths, etc.).
    
    Args:
        path: File path to normalize
        
    Returns:
        Normalized absolute path
    """
    return str(Path(path).expanduser().resolve())


def get_relative_path(file_path: str, base_directory: str) -> str:
    """
    Get relative path from base directory to file.
    
    Args:
        file_path: Full path to file
        base_directory: Base directory
        
    Returns:
        Relative path
    """
    try:
        return os.path.relpath(file_path, base_directory)
    except ValueError:
        # Paths are on different drives (Windows)
        return file_path
