"""
Configuration Service - Handles configuration management and persistence

Supports two-file configuration system:
- Private settings (.env) - API keys, URLs, secrets
- Public settings (config.json) - Application features, UI preferences
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.config.config_manager import (
    load_env_file, load_config_file, save_config_file,
    update_public_config, update_private_config, get_combined_config
)
    
class ConfigService:
    """Service for handling configuration management"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.env_file = os.path.join(project_root, '.env')
        self.config_file = os.path.join(project_root, 'config.json')
        
        # Load environment variables
        load_env_file(project_root)
    
    def get_config(self) -> Dict[str, Any]:
        """Get combined configuration from both .env and config.json"""
        # Get combined configuration
        combined = get_combined_config(self.project_root)
        
        # Flatten for backward compatibility
        config = {}
        
        # Add public settings
        public = combined.get('public', {})
        clip_config = public.get('clip_config', {})
        analysis_features = public.get('analysis_features', {})
        ui_settings = public.get('ui_settings', {})
        file_handling = public.get('file_handling', {})
        
        config.update({
            'API_BASE_URL': clip_config.get('api_base_url', 'http://localhost:7860'),
            'CLIP_MODEL_NAME': clip_config.get('model_name', 'ViT-L-14/openai'),
            'ENABLE_CLIP_ANALYSIS': clip_config.get('enable_clip_analysis', True),
            'ENABLE_LLM_ANALYSIS': analysis_features.get('enable_llm_analysis', True),
            'ENABLE_PARALLEL_PROCESSING': analysis_features.get('enable_parallel_processing', False),
            'ENABLE_METADATA_EXTRACTION': analysis_features.get('enable_metadata_extraction', True),
            'IMAGE_DIRECTORY': 'Images',  # Default
            'OUTPUT_DIRECTORY': 'Output',  # Default
            'WEB_PORT': combined['private'].get('web_port', 5050),
            'CLIP_MODES': clip_config.get('clip_modes', ['best', 'fast', 'classic']),
            'PROMPT_CHOICES': clip_config.get('prompt_choices', ['P1', 'P2']),
            'DEBUG': False,  # Default
            'FORCE_REPROCESS': False,  # Default
            'GENERATE_SUMMARIES': analysis_features.get('generate_summaries', True)
        })
        
        return config
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update configuration in appropriate files"""
        try:
            # Separate private and public settings
            private_settings = {}
            public_settings = {}
            
            # Define which settings go where
            private_keys = {
                'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'OLLAMA_API_KEY',
                'OPENAI_URL', 'ANTHROPIC_URL', 'GOOGLE_URL', 'OLLAMA_URL',
                'DATABASE_URL', 'WEB_PORT', 'SECRET_KEY'
            }
            
            for key, value in config_data.items():
                if key in private_keys:
                    private_settings[key] = str(value)
                else:
                    # Map old keys to new structure
                    if key == 'API_BASE_URL':
                        public_settings.setdefault('clip_config', {})['api_base_url'] = value
                    elif key == 'CLIP_MODEL_NAME':
                        public_settings.setdefault('clip_config', {})['model_name'] = value
                    elif key == 'ENABLE_CLIP_ANALYSIS':
                        public_settings.setdefault('clip_config', {})['enable_clip_analysis'] = value
                    elif key == 'ENABLE_LLM_ANALYSIS':
                        public_settings.setdefault('analysis_features', {})['enable_llm_analysis'] = value
                    elif key == 'ENABLE_PARALLEL_PROCESSING':
                        public_settings.setdefault('analysis_features', {})['enable_parallel_processing'] = value
                    elif key == 'ENABLE_METADATA_EXTRACTION':
                        public_settings.setdefault('analysis_features', {})['enable_metadata_extraction'] = value
                    elif key == 'GENERATE_SUMMARIES':
                        public_settings.setdefault('analysis_features', {})['generate_summaries'] = value
                    elif key == 'CLIP_MODES':
                        public_settings.setdefault('clip_config', {})['clip_modes'] = value if isinstance(value, list) else value.split(',')
                    elif key == 'PROMPT_CHOICES':
                        public_settings.setdefault('clip_config', {})['prompt_choices'] = value if isinstance(value, list) else value.split(',')
                    else:
                        # Add to public settings as-is
                        public_settings[key] = value
            
            # Update private settings (.env)
            if private_settings:
                if not update_private_config(private_settings, self.project_root):
                    print("Warning: Failed to update private settings")
            
            # Update public settings (config.json)
            if public_settings:
                if not update_public_config(public_settings, self.project_root):
                    print("Warning: Failed to update public settings")
            
            # Reload environment variables
            load_env_file(self.project_root)
            
            print("Configuration updated successfully")
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get configuration for image processing"""
        config = self.get_config()
        return {
            'API_BASE_URL': config['API_BASE_URL'],
            'CLIP_MODEL_NAME': config['CLIP_MODEL_NAME'],
            'ENABLE_CLIP_ANALYSIS': config['ENABLE_CLIP_ANALYSIS'],
            'ENABLE_LLM_ANALYSIS': config['ENABLE_LLM_ANALYSIS'],
            'ENABLE_PARALLEL_PROCESSING': config['ENABLE_PARALLEL_PROCESSING'],
            'ENABLE_METADATA_EXTRACTION': config['ENABLE_METADATA_EXTRACTION'],
            'IMAGE_DIRECTORY': os.path.join(self.project_root, config['IMAGE_DIRECTORY']),
            'OUTPUT_DIRECTORY': os.path.join(self.project_root, config['OUTPUT_DIRECTORY']),
            'CLIP_MODES': config['CLIP_MODES'],
            'PROMPT_CHOICES': config['PROMPT_CHOICES'],
            'DEBUG': config['DEBUG'],
            'FORCE_REPROCESS': config['FORCE_REPROCESS'],
            'GENERATE_SUMMARIES': config['GENERATE_SUMMARIES']
        }
    
    def validate_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration data"""
        errors = []
        
        # Validate required fields
        required_fields = ['API_BASE_URL', 'CLIP_MODEL_NAME']
        for field in required_fields:
            if field not in config_data or not config_data[field]:
                errors.append(f"{field} is required")
        
        # Validate port number
        if 'WEB_PORT' in config_data:
            try:
                port = int(config_data['WEB_PORT'])
                if port < 1024 or port > 65535:
                    errors.append("WEB_PORT must be between 1024 and 65535")
            except ValueError:
                errors.append("WEB_PORT must be a valid number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        } 