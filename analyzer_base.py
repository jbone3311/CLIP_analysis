"""
Base analyzer interface for image analysis components.

Provides a common interface for different types of image analyzers
and includes shared functionality for validation, error handling, and logging.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Protocol
from pathlib import Path
import logging
import time
from functools import wraps

from input_validation import validate_image_file, ValidationError
from exceptions import (
    ImageAnalysisError, ProcessingError, TimeoutError,
    safe_error_message, log_error_context
)

logger = logging.getLogger(__name__)

def track_performance(func):
    """Decorator to track analyzer performance metrics."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        method_name = f"{self.__class__.__name__}.{func.__name__}"
        
        try:
            logger.debug(f"Starting {method_name}")
            result = func(self, *args, **kwargs)
            
            duration = time.time() - start_time
            logger.info(f"{method_name} completed successfully in {duration:.2f}s")
            
            # Store performance metrics
            if not hasattr(self, '_performance_metrics'):
                self._performance_metrics = {}
            self._performance_metrics[method_name] = {
                'duration': duration,
                'timestamp': start_time,
                'success': True
            }
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{method_name} failed after {duration:.2f}s: {safe_error_message(e)}")
            
            # Store failure metrics
            if not hasattr(self, '_performance_metrics'):
                self._performance_metrics = {}
            self._performance_metrics[method_name] = {
                'duration': duration,
                'timestamp': start_time,
                'success': False,
                'error': str(e)
            }
            
            raise
    
    return wrapper

class AnalyzerProtocol(Protocol):
    """Protocol defining the interface for analyzers."""
    
    def process_image(self, image_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a single image."""
        ...
    
    def create_error_result(self, error: Exception, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Create standardized error result."""
        ...

class BaseAnalyzer(ABC):
    """
    Abstract base class for image analyzers.
    
    Provides common functionality for validation, error handling,
    and result formatting that all analyzers should implement.
    """
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        """
        Initialize base analyzer.
        
        Args:
            config: Configuration dictionary
            name: Optional name for the analyzer instance
        """
        self.config = config
        self.name = name or self.__class__.__name__
        self._performance_metrics = {}
        
        # Validate configuration
        self._validate_config()
        
        logger.info(f"Initialized {self.name} analyzer")
    
    def _validate_config(self) -> None:
        """Validate analyzer configuration."""
        required_configs = self.get_required_config_keys()
        missing_configs = [key for key in required_configs if key not in self.config]
        
        if missing_configs:
            raise ValidationError(
                f"Missing required configuration keys for {self.name}: {missing_configs}"
            )
    
    @abstractmethod
    def get_required_config_keys(self) -> List[str]:
        """
        Return list of required configuration keys.
        
        Returns:
            List of required configuration key names
        """
        pass
    
    @abstractmethod
    def analyze_image(self, image_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Analyze a single image.
        
        Args:
            image_path: Path to image file
            **kwargs: Additional analyzer-specific arguments
            
        Returns:
            Analysis results dictionary
            
        Raises:
            ImageAnalysisError: If analysis fails
        """
        pass
    
    @track_performance
    def process_image(self, image_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Process image with validation and error handling.
        
        Args:
            image_path: Path to image file
            **kwargs: Additional processing arguments
            
        Returns:
            Processing results dictionary with metadata
            
        Raises:
            ValidationError: If image validation fails
            ProcessingError: If processing fails
        """
        try:
            # Validate input image
            validated_path, file_size, mime_type = validate_image_file(str(image_path))
            
            logger.info(f"Processing image: {validated_path} ({file_size/1024:.1f}KB, {mime_type})")
            
            # Perform analysis
            analysis_result = self.analyze_image(validated_path, **kwargs)
            
            # Create standardized result format
            result = {
                'analyzer': self.name,
                'image_path': str(validated_path),
                'file_size': file_size,
                'mime_type': mime_type,
                'timestamp': time.time(),
                'success': True,
                'analysis': analysis_result
            }
            
            logger.info(f"Successfully processed image: {validated_path}")
            return result
            
        except ValidationError as e:
            log_error_context(e, {'image_path': str(image_path), 'analyzer': self.name})
            raise
            
        except Exception as e:
            error_msg = f"Failed to process image {image_path}"
            log_error_context(e, {'image_path': str(image_path), 'analyzer': self.name})
            raise ProcessingError(error_msg, stage='image_processing') from e
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this analyzer.
        
        Returns:
            Dictionary of performance metrics
        """
        return self._performance_metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self._performance_metrics = {}
        logger.debug(f"Reset performance metrics for {self.name}")
    
    def validate_output_format(self, result: Dict[str, Any]) -> bool:
        """
        Validate output format consistency.
        
        Args:
            result: Analysis result to validate
            
        Returns:
            True if format is valid
            
        Raises:
            ValidationError: If format is invalid
        """
        required_fields = ['analyzer', 'image_path', 'timestamp', 'success']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            raise ValidationError(f"Missing required output fields: {missing_fields}")
        
        if not isinstance(result.get('success'), bool):
            raise ValidationError("'success' field must be boolean")
        
        if result['success'] and 'analysis' not in result:
            raise ValidationError("Successful results must include 'analysis' field")
        
        return True
    
    def create_error_result(self, error: Exception, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Create standardized error result.
        
        Args:
            error: Exception that occurred
            image_path: Path to image that caused error
            
        Returns:
            Standardized error result dictionary
        """
        return {
            'analyzer': self.name,
            'image_path': str(image_path),
            'timestamp': time.time(),
            'success': False,
            'error': safe_error_message(error),
            'error_type': type(error).__name__
        }
    
    def process_batch(self, image_paths: List[Union[str, Path]], 
                     continue_on_error: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple images in batch.
        
        Args:
            image_paths: List of image paths to process
            continue_on_error: Whether to continue processing if one image fails
            **kwargs: Additional processing arguments
            
        Returns:
            List of processing results
        """
        results = []
        processed_count = 0
        error_count = 0
        
        logger.info(f"Starting batch processing of {len(image_paths)} images")
        
        for i, image_path in enumerate(image_paths):
            try:
                result = self.process_image(image_path, **kwargs)
                results.append(result)
                processed_count += 1
                
                if i % 10 == 0:  # Log progress every 10 images
                    logger.info(f"Batch progress: {i+1}/{len(image_paths)} images processed")
                    
            except Exception as e:
                error_count += 1
                error_result = self.create_error_result(e, image_path)
                results.append(error_result)
                
                if continue_on_error:
                    logger.warning(f"Error processing {image_path}, continuing: {safe_error_message(e)}")
                else:
                    logger.error(f"Error processing {image_path}, stopping batch: {safe_error_message(e)}")
                    break
        
        logger.info(
            f"Batch processing completed: {processed_count} successful, "
            f"{error_count} errors out of {len(image_paths)} total"
        )
        
        return results
    
    def __str__(self) -> str:
        """String representation of analyzer."""
        return f"{self.name}(config_keys={list(self.config.keys())})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', config={self.config})"