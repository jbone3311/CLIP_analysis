#!/usr/bin/env python3
"""
Configuration Models - Typed Dataclasses for Configuration

Provides type-safe configuration models using dataclasses.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class CLIPConfig:
    """CLIP API configuration"""
    api_url: str = "http://localhost:7860"
    api_password: Optional[str] = None
    model_name: str = "ViT-L-14/openai"
    modes: List[str] = field(default_factory=lambda: ["best", "fast", "classic", "negative", "caption"])
    timeout: int = 300


@dataclass
class LLMConfig:
    """LLM API configuration"""
    openai_api_key: Optional[str] = None
    openai_url: str = "https://api.openai.com/v1"
    anthropic_api_key: Optional[str] = None
    anthropic_url: str = "https://api.anthropic.com/v1"
    google_api_key: Optional[str] = None
    google_url: str = "https://generativelanguage.googleapis.com/v1"
    grok_api_key: Optional[str] = None
    grok_url: str = "https://api.x.ai/v1"
    cohere_api_key: Optional[str] = None
    cohere_url: str = "https://api.cohere.ai/v1"
    mistral_api_key: Optional[str] = None
    mistral_url: str = "https://api.mistral.ai/v1"
    perplexity_api_key: Optional[str] = None
    perplexity_url: str = "https://api.perplexity.ai"
    ollama_url: str = "http://localhost:11434"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "image_analysis.db"
    url: str = "sqlite:///image_analysis.db"


@dataclass
class WebConfig:
    """Web server configuration"""
    port: int = 5050
    secret_key: str = "change_this_in_production"
    flask_secret_key: str = "change_this_in_production"
    host: str = "0.0.0.0"
    debug: bool = False


@dataclass
class AnalysisConfig:
    """Analysis feature flags"""
    enable_clip_analysis: bool = True
    enable_llm_analysis: bool = True
    enable_metadata_extraction: bool = True
    enable_parallel_processing: bool = False
    generate_summaries: bool = True
    force_reprocess: bool = False


@dataclass
class DirectoryConfig:
    """Directory configuration"""
    image_directory: str = "Images"
    output_directory: str = "Output"
    log_directory: str = "logs"


@dataclass
class AppConfig:
    """
    Complete application configuration.
    
    This is the main configuration dataclass that combines all configuration sections.
    """
    clip: CLIPConfig = field(default_factory=CLIPConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    web: WebConfig = field(default_factory=WebConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    directories: DirectoryConfig = field(default_factory=DirectoryConfig)
    debug: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create AppConfig from dictionary"""
        return cls(
            clip=CLIPConfig(**data.get("clip", {})),
            llm=LLMConfig(**data.get("llm", {})),
            database=DatabaseConfig(**data.get("database", {})),
            web=WebConfig(**data.get("web", {})),
            analysis=AnalysisConfig(**data.get("analysis", {})),
            directories=DirectoryConfig(**data.get("directories", {})),
            debug=data.get("debug", False),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AppConfig to dictionary"""
        return {
            "clip": {
                "api_url": self.clip.api_url,
                "api_password": self.clip.api_password,
                "model_name": self.clip.model_name,
                "modes": self.clip.modes,
                "timeout": self.clip.timeout,
            },
            "llm": {
                "openai_api_key": self.llm.openai_api_key,
                "openai_url": self.llm.openai_url,
                "anthropic_api_key": self.llm.anthropic_api_key,
                "anthropic_url": self.llm.anthropic_url,
                "google_api_key": self.llm.google_api_key,
                "google_url": self.llm.google_url,
                "grok_api_key": self.llm.grok_api_key,
                "grok_url": self.llm.grok_url,
                "cohere_api_key": self.llm.cohere_api_key,
                "cohere_url": self.llm.cohere_url,
                "mistral_api_key": self.llm.mistral_api_key,
                "mistral_url": self.llm.mistral_url,
                "perplexity_api_key": self.llm.perplexity_api_key,
                "perplexity_url": self.llm.perplexity_url,
                "ollama_url": self.llm.ollama_url,
            },
            "database": {
                "path": self.database.path,
                "url": self.database.url,
            },
            "web": {
                "port": self.web.port,
                "secret_key": self.web.secret_key,
                "flask_secret_key": self.web.flask_secret_key,
                "host": self.web.host,
                "debug": self.web.debug,
            },
            "analysis": {
                "enable_clip_analysis": self.analysis.enable_clip_analysis,
                "enable_llm_analysis": self.analysis.enable_llm_analysis,
                "enable_metadata_extraction": self.analysis.enable_metadata_extraction,
                "enable_parallel_processing": self.analysis.enable_parallel_processing,
                "generate_summaries": self.analysis.generate_summaries,
                "force_reprocess": self.analysis.force_reprocess,
            },
            "directories": {
                "image_directory": self.directories.image_directory,
                "output_directory": self.directories.output_directory,
                "log_directory": self.directories.log_directory,
            },
            "debug": self.debug,
        }
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """
        Convert to legacy dictionary format for backward compatibility.
        This maintains compatibility with code expecting os.getenv() style keys.
        """
        return {
            # CLIP config
            "CLIP_API_URL": self.clip.api_url,
            "CLIP_API_PASSWORD": self.clip.api_password,
            "CLIP_MODEL_NAME": self.clip.model_name,
            "CLIP_MODES": self.clip.modes,
            "CLIP_API_TIMEOUT": self.clip.timeout,
            "API_BASE_URL": self.clip.api_url,  # Legacy support
            
            # LLM config
            "OPENAI_API_KEY": self.llm.openai_api_key or "",
            "OPENAI_URL": self.llm.openai_url,
            "ANTHROPIC_API_KEY": self.llm.anthropic_api_key or "",
            "ANTHROPIC_URL": self.llm.anthropic_url,
            "GOOGLE_API_KEY": self.llm.google_api_key or "",
            "GOOGLE_URL": self.llm.google_url,
            "GROK_API_KEY": self.llm.grok_api_key or "",
            "GROK_URL": self.llm.grok_url,
            "COHERE_API_KEY": self.llm.cohere_api_key or "",
            "COHERE_URL": self.llm.cohere_url,
            "MISTRAL_API_KEY": self.llm.mistral_api_key or "",
            "MISTRAL_URL": self.llm.mistral_url,
            "PERPLEXITY_API_KEY": self.llm.perplexity_api_key or "",
            "PERPLEXITY_URL": self.llm.perplexity_url,
            "OLLAMA_URL": self.llm.ollama_url,
            
            # Database config
            "DATABASE_PATH": self.database.path,
            "DATABASE_URL": self.database.url,
            
            # Web config
            "WEB_PORT": self.web.port,
            "SECRET_KEY": self.web.secret_key,
            "FLASK_SECRET_KEY": self.web.flask_secret_key,
            
            # Analysis flags
            "ENABLE_CLIP_ANALYSIS": self.analysis.enable_clip_analysis,
            "ENABLE_LLM_ANALYSIS": self.analysis.enable_llm_analysis,
            "ENABLE_METADATA_EXTRACTION": self.analysis.enable_metadata_extraction,
            "ENABLE_PARALLEL_PROCESSING": self.analysis.enable_parallel_processing,
            "GENERATE_SUMMARIES": self.analysis.generate_summaries,
            "FORCE_REPROCESS": self.analysis.force_reprocess,
            
            # Directories
            "IMAGE_DIRECTORY": self.directories.image_directory,
            "OUTPUT_DIRECTORY": self.directories.output_directory,
            
            # Debug
            "DEBUG": self.debug or self.web.debug,
        }

