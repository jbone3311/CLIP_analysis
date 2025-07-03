"""
Analyzer factory for creating and managing image analysis components.

Implements the factory pattern to create different types of analyzers
with proper configuration injection and validation.
"""

from typing import Dict, Any, List, Optional, Union, Type
import logging
from enum import Enum

from analyzer_base import BaseAnalyzer
from llm_analyzer import LLMAnalyzer
from clip_analyzer import CLIPAnalyzer
from config_manager import ConfigurationManager, LLMConfig, CLIPConfig
from exceptions import ConfigurationError, ValidationError

logger = logging.getLogger(__name__)

class AnalyzerType(Enum):
    """Enumeration of supported analyzer types."""
    LLM = "llm"
    CLIP = "clip"

class AnalyzerFactory:
    """
    Factory for creating and managing image analyzers.
    
    Provides centralized creation of analyzers with proper configuration
    injection and validation.
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        """
        Initialize analyzer factory.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        
        # Registry of available analyzer classes
        self._analyzer_classes: Dict[AnalyzerType, Type[BaseAnalyzer]] = {
            AnalyzerType.LLM: LLMAnalyzer,
            AnalyzerType.CLIP: CLIPAnalyzer
        }
        
        logger.debug("Analyzer factory initialized")
    
    def create_llm_analyzer(self, llm_index: int = 0, 
                           custom_config: Optional[Dict[str, Any]] = None) -> LLMAnalyzer:
        """
        Create LLM analyzer instance.
        
        Args:
            llm_index: Index of LLM configuration to use (0-based)
            custom_config: Optional custom configuration overrides
            
        Returns:
            Configured LLM analyzer instance
            
        Raises:
            ConfigurationError: If LLM configuration is invalid
        """
        llm_config = self.config_manager.get_llm_config(llm_index)
        if not llm_config:
            raise ConfigurationError(f"No LLM configuration found at index {llm_index}")
        
        # Convert dataclass to dictionary for analyzer
        config_dict = {
            'api_url': llm_config.api_url,
            'api_key': llm_config.api_key,
            'model_name': llm_config.model_name,
            'timeout': llm_config.timeout,
            'retry_limit': llm_config.retry_limit,
            'min_request_interval': llm_config.min_request_interval,
            'prompts_file': 'LLM_Prompts.json'  # Default prompts file
        }
        
        # Apply custom configuration overrides
        if custom_config:
            config_dict.update(custom_config)
        
        try:
            analyzer = LLMAnalyzer(config_dict, name=f"LLM_{llm_config.title}")
            logger.info(f"Created LLM analyzer: {llm_config.title}")
            return analyzer
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create LLM analyzer: {e}") from e
    
    def create_clip_analyzer(self, custom_config: Optional[Dict[str, Any]] = None) -> CLIPAnalyzer:
        """
        Create CLIP analyzer instance.
        
        Args:
            custom_config: Optional custom configuration overrides
            
        Returns:
            Configured CLIP analyzer instance
            
        Raises:
            ConfigurationError: If CLIP configuration is invalid
        """
        clip_config = self.config_manager.clip_config
        
        # Convert dataclass to dictionary for analyzer
        config_dict = {
            'api_base_url': clip_config.api_base_url,
            'model_name': clip_config.model_name,
            'timeout': clip_config.timeout,
            'retry_limit': clip_config.retry_limit,
            'min_request_interval': clip_config.min_request_interval,
            'default_modes': clip_config.default_modes
        }
        
        # Apply custom configuration overrides
        if custom_config:
            config_dict.update(custom_config)
        
        try:
            analyzer = CLIPAnalyzer(config_dict, name="CLIP_Analyzer")
            logger.info(f"Created CLIP analyzer: {clip_config.model_name}")
            return analyzer
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create CLIP analyzer: {e}") from e
    
    def create_analyzer(self, analyzer_type: Union[AnalyzerType, str],
                       index: int = 0,
                       custom_config: Optional[Dict[str, Any]] = None) -> BaseAnalyzer:
        """
        Create analyzer of specified type.
        
        Args:
            analyzer_type: Type of analyzer to create
            index: Index for LLM analyzers (ignored for CLIP)
            custom_config: Optional custom configuration overrides
            
        Returns:
            Configured analyzer instance
            
        Raises:
            ConfigurationError: If analyzer creation fails
            ValidationError: If analyzer type is invalid
        """
        # Convert string to enum if needed
        if isinstance(analyzer_type, str):
            try:
                analyzer_type = AnalyzerType(analyzer_type.lower())
            except ValueError:
                raise ValidationError(f"Unknown analyzer type: {analyzer_type}")
        
        if analyzer_type == AnalyzerType.LLM:
            return self.create_llm_analyzer(index, custom_config)
        elif analyzer_type == AnalyzerType.CLIP:
            return self.create_clip_analyzer(custom_config)
        else:
            raise ValidationError(f"Unsupported analyzer type: {analyzer_type}")
    
    def create_all_llm_analyzers(self) -> List[LLMAnalyzer]:
        """
        Create all configured LLM analyzers.
        
        Returns:
            List of configured LLM analyzer instances
        """
        analyzers = []
        
        for i, llm_config in enumerate(self.config_manager.llm_configs):
            try:
                analyzer = self.create_llm_analyzer(i)
                analyzers.append(analyzer)
            except Exception as e:
                logger.error(f"Failed to create LLM analyzer {i} ({llm_config.title}): {e}")
        
        logger.info(f"Created {len(analyzers)} LLM analyzers")
        return analyzers
    
    def create_dual_analyzer_pipeline(self) -> Dict[str, BaseAnalyzer]:
        """
        Create a complete dual-analyzer pipeline with both LLM and CLIP.
        
        Returns:
            Dictionary containing both analyzer types
            
        Raises:
            ConfigurationError: If neither analyzer type can be created
        """
        pipeline = {}
        
        # Try to create CLIP analyzer
        try:
            clip_analyzer = self.create_clip_analyzer()
            pipeline['clip'] = clip_analyzer
        except Exception as e:
            logger.warning(f"Failed to create CLIP analyzer: {e}")
        
        # Try to create at least one LLM analyzer
        try:
            llm_analyzer = self.create_llm_analyzer(0)
            pipeline['llm'] = llm_analyzer
        except Exception as e:
            logger.warning(f"Failed to create primary LLM analyzer: {e}")
        
        if not pipeline:
            raise ConfigurationError("Failed to create any analyzers for pipeline")
        
        logger.info(f"Created dual analyzer pipeline with {list(pipeline.keys())}")
        return pipeline
    
    def validate_analyzer_configs(self) -> Dict[str, List[str]]:
        """
        Validate all analyzer configurations.
        
        Returns:
            Dictionary of validation results by analyzer type
        """
        validation_results = {
            'llm': [],
            'clip': [],
            'general': []
        }
        
        # Validate LLM configurations
        for i, llm_config in enumerate(self.config_manager.llm_configs):
            try:
                # Test creating the analyzer (without actual instantiation)
                config_dict = {
                    'api_url': llm_config.api_url,
                    'model_name': llm_config.model_name,
                    'api_key': llm_config.api_key
                }
                
                # Basic validation
                if not llm_config.api_key and 'localhost' not in llm_config.api_url:
                    validation_results['llm'].append(
                        f"LLM {i+1} ({llm_config.title}): Missing API key for external service"
                    )
                
                if not llm_config.api_url.startswith(('http://', 'https://')):
                    validation_results['llm'].append(
                        f"LLM {i+1} ({llm_config.title}): Invalid API URL format"
                    )
                    
            except Exception as e:
                validation_results['llm'].append(
                    f"LLM {i+1} ({llm_config.title}): Configuration error - {e}"
                )
        
        # Validate CLIP configuration
        try:
            clip_config = self.config_manager.clip_config
            
            if not clip_config.api_base_url.startswith(('http://', 'https://')):
                validation_results['clip'].append("Invalid CLIP API URL format")
                
            # Test if modes are valid
            valid_modes = CLIPAnalyzer.SUPPORTED_MODES
            invalid_modes = [mode for mode in clip_config.default_modes if mode not in valid_modes]
            if invalid_modes:
                validation_results['clip'].append(f"Invalid CLIP modes: {invalid_modes}")
                
        except Exception as e:
            validation_results['clip'].append(f"CLIP configuration error: {e}")
        
        # General validation
        if not self.config_manager.llm_configs and not self.config_manager.clip_config.api_base_url:
            validation_results['general'].append("No analyzers configured")
        
        return validation_results
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """
        Get information about available analyzers.
        
        Returns:
            Dictionary containing analyzer information
        """
        return {
            'llm_analyzers': [
                {
                    'index': i,
                    'title': config.title,
                    'model': config.model_name,
                    'api_url': config.api_url,
                    'has_api_key': bool(config.api_key)
                }
                for i, config in enumerate(self.config_manager.llm_configs)
            ],
            'clip_analyzer': {
                'model': self.config_manager.clip_config.model_name,
                'api_url': self.config_manager.clip_config.api_base_url,
                'default_modes': self.config_manager.clip_config.default_modes
            },
            'supported_types': [analyzer_type.value for analyzer_type in AnalyzerType]
        }
    
    def test_analyzer_connections(self) -> Dict[str, Dict[str, Any]]:
        """
        Test connections to all configured analyzers.
        
        Returns:
            Dictionary of connection test results
        """
        results = {
            'llm': {},
            'clip': {}
        }
        
        # Test LLM analyzers
        for i, llm_config in enumerate(self.config_manager.llm_configs):
            try:
                analyzer = self.create_llm_analyzer(i)
                # Note: LLM analyzers don't have a test_connection method
                # This would require implementing one or making a lightweight test request
                results['llm'][f'llm_{i}'] = {
                    'title': llm_config.title,
                    'status': 'configured',
                    'has_api_key': bool(llm_config.api_key)
                }
            except Exception as e:
                results['llm'][f'llm_{i}'] = {
                    'title': llm_config.title,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Test CLIP analyzer
        try:
            clip_analyzer = self.create_clip_analyzer()
            connection_result = clip_analyzer.test_connection()
            results['clip']['clip_analyzer'] = connection_result
        except Exception as e:
            results['clip']['clip_analyzer'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return results

# Convenience functions for common factory operations

def create_analyzer_from_config(config_manager: ConfigurationManager,
                               analyzer_type: Union[AnalyzerType, str],
                               index: int = 0) -> BaseAnalyzer:
    """
    Convenience function to create analyzer from configuration.
    
    Args:
        config_manager: Configuration manager instance
        analyzer_type: Type of analyzer to create
        index: Index for LLM analyzers
        
    Returns:
        Configured analyzer instance
    """
    factory = AnalyzerFactory(config_manager)
    return factory.create_analyzer(analyzer_type, index)

def create_dual_pipeline(config_manager: ConfigurationManager) -> Dict[str, BaseAnalyzer]:
    """
    Convenience function to create dual analyzer pipeline.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Dictionary containing both analyzer types
    """
    factory = AnalyzerFactory(config_manager)
    return factory.create_dual_analyzer_pipeline()