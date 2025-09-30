"""
Directory Processor Module

Handles batch processing of images in directories using CLIP and LLM analysis.
Refactored with dependency injection and extracted utilities.
"""

import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import sys

# Load environment variables
load_dotenv()

# Import analyzers
from src.analyzers.clip_analyzer import analyze_image_with_clip
from src.analyzers.llm_manager import LLMManager
from src.analyzers.metadata_extractor import extract_metadata

# Import database
from src.database.db_manager import DatabaseManager

# Import utilities
from src.utils import (
    get_global_logger,
    compute_file_hash,
    find_image_files,
    ProgressTracker,
    ErrorCategory,
    error_context,
    handle_errors
)

# Get logger
logger = get_global_logger()


class UnifiedAnalysisResult:
    """Represents a unified analysis result for a single image"""
    
    def __init__(self, image_path: str, config: Dict[str, Any]):
        """
        Initialize analysis result container.
        
        Args:
            image_path: Path to the image file
            config: Configuration dictionary
        """
        self.image_path = image_path
        self.config = config
        self.filename = os.path.basename(image_path)
        self.directory = os.path.dirname(image_path).replace("\\", "/")
        self.md5 = compute_file_hash(image_path, algorithm='md5')
        self.date_added = datetime.now().isoformat()
        
        # Initialize result structure
        self.result = {
            "file_info": {
                "filename": self.filename,
                "directory": self.directory,
                "date_added": self.date_added,
                "date_processed": self.date_added,
                "md5": self.md5,
                "file_size": os.path.getsize(image_path) if os.path.exists(image_path) else 0
            },
            "analysis": {
                "clip": {},
                "llm": {},
                "metadata": {}
            },
            "processing_info": {
                "config_used": {
                    "clip_enabled": config.get('ENABLE_CLIP_ANALYSIS', False),
                    "llm_enabled": config.get('ENABLE_LLM_ANALYSIS', False),
                    "clip_modes": config.get('CLIP_MODES', []),
                    "llm_models": [m['number'] for m in config.get('llm_models', [])],
                    "prompt_choices": config.get('PROMPT_CHOICES', [])
                },
                "processing_time": 0,
                "status": "pending",
                "errors": []
            }
        }
    
    def add_clip_result(self, clip_result: Dict[str, Any]) -> None:
        """Add CLIP analysis results"""
        if clip_result.get("status") == "success":
            self.result["analysis"]["clip"] = clip_result.get("prompt", {})
        else:
            self.result["processing_info"]["errors"].append({
                "type": "clip",
                "error": clip_result.get("message", "Unknown CLIP error")
            })
    
    def add_llm_results(self, llm_results: Dict[str, Any]) -> None:
        """Add multiple LLM analysis results"""
        self.result["analysis"]["llm"] = llm_results
    
    def add_metadata(self, metadata: Dict[str, Any]) -> None:
        """Add image metadata"""
        self.result["analysis"]["metadata"] = metadata
    
    def mark_complete(self, processing_time: float) -> None:
        """Mark analysis as complete"""
        self.result["processing_info"]["processing_time"] = processing_time
        self.result["processing_info"]["status"] = "complete"
        self.result["file_info"]["date_processed"] = datetime.now().isoformat()
    
    def mark_failed(self, error: str) -> None:
        """Mark analysis as failed"""
        self.result["processing_info"]["status"] = "failed"
        self.result["processing_info"]["errors"].append({
            "type": "general",
            "error": error
        })
    
    def save(self, output_directory: str) -> str:
        """Save the unified result to a JSON file"""
        base_filename = os.path.splitext(self.filename)[0]
        output_path = os.path.join(output_directory, f"{base_filename}_analysis.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.result, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved unified analysis result to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return ""


class DirectoryProcessor:
    """
    Processes directories of images with CLIP and LLM analysis.
    
    Refactored with dependency injection for better testability and modularity.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        db_manager: Optional[DatabaseManager] = None,
        llm_manager: Optional[LLMManager] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize DirectoryProcessor with dependency injection.
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance (created if not provided)
            llm_manager: LLM manager instance (created if not provided)
            progress_callback: Optional callback for progress messages
        """
        self.config = config
        self.db_manager = db_manager or DatabaseManager()
        self.llm_manager = llm_manager or LLMManager()
        self.progress_callback = progress_callback
        
        # Use database for LLM models
        self.llm_models = self.db_manager.get_llm_models() if self.config['ENABLE_LLM_ANALYSIS'] else []
        self.config['llm_models'] = self.llm_models  # Add to config for reference
        
        # Validate configuration
        self._validate_config()
        
        logger.info("DirectoryProcessor initialized with config", data={'config': str(self.config)})
        logger.debug(f"CLIP Analysis Enabled: {self.config['ENABLE_CLIP_ANALYSIS']}")
        logger.debug(f"LLM Analysis Enabled: {self.config['ENABLE_LLM_ANALYSIS']}")
        logger.debug(f"Available LLM Models: {[m['name'] for m in self.llm_models]}")
        logger.info("Database integration enabled")

    def _validate_config(self) -> None:
        """Validate configuration and provide helpful error messages"""
        errors = []
        
        if not os.path.exists(self.config['IMAGE_DIRECTORY']):
            errors.append(f"Image directory '{self.config['IMAGE_DIRECTORY']}' does not exist")
        
        if not os.path.exists(self.config['OUTPUT_DIRECTORY']):
            try:
                os.makedirs(self.config['OUTPUT_DIRECTORY'])
                logger.info(f"Created output directory: {self.config['OUTPUT_DIRECTORY']}")
            except Exception as e:
                errors.append(f"Cannot create output directory '{self.config['OUTPUT_DIRECTORY']}': {e}")
        
        if self.config['ENABLE_CLIP_ANALYSIS']:
            if not self.config.get('API_BASE_URL'):
                errors.append("CLIP analysis enabled but API_BASE_URL not configured")
            if not self.config.get('CLIP_MODEL_NAME'):
                errors.append("CLIP analysis enabled but CLIP_MODEL_NAME not configured")
        
        if self.config['ENABLE_LLM_ANALYSIS'] and not self.llm_models:
            errors.append("LLM analysis enabled but no LLM models configured")
        
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   • {error}")
            print("\nPlease check your .env file and try again.")
            sys.exit(1)

    def process_directory(self) -> None:
        """Process all images in the directory with progress tracking"""
        image_files = find_image_files(self.config['IMAGE_DIRECTORY'], recursive=True)
        
        if not image_files:
            print(f"[ERROR] No image files found in {self.config['IMAGE_DIRECTORY']}")
            return
        
        print(f"[START] Starting analysis of {len(image_files)} images...")
        print(f"[DIR] Input directory: {self.config['IMAGE_DIRECTORY']}")
        print(f"[DIR] Output directory: {self.config['OUTPUT_DIRECTORY']}")
        print(f"[CLIP] CLIP Analysis: {'[ENABLED]' if self.config['ENABLE_CLIP_ANALYSIS'] else '[DISABLED]'}")
        if self.config['ENABLE_CLIP_ANALYSIS']:
            print(f"[CLIP] CLIP Modes: {', '.join(self.config['CLIP_MODES'])}")
            print(f"[CLIP] CLIP Model: {self.config['CLIP_MODEL_NAME']}")
        print(f"[LLM] LLM Analysis: {'[ENABLED]' if self.config['ENABLE_LLM_ANALYSIS'] else '[DISABLED]'}")
        print(f"[META] Metadata Extraction: {'[ENABLED]' if self.config.get('ENABLE_METADATA_EXTRACTION', True) else '[DISABLED]'}")
        print(f"[PARALLEL] Parallel Processing: {'[ENABLED]' if self.config['ENABLE_PARALLEL_PROCESSING'] else '[DISABLED]'}")
        print()

        progress = ProgressTracker(
            total=len(image_files),
            callback=self.progress_callback
        )
        
        if self.config['ENABLE_PARALLEL_PROCESSING']:
            self._process_parallel(image_files, progress)
        else:
            self._process_sequential(image_files, progress)
        
        progress.finish()
        self._generate_summaries()

    def _process_sequential(self, image_files: List[str], progress: ProgressTracker) -> None:
        """Process images sequentially"""
        for image_file in image_files:
            try:
                self.process_image(image_file, progress)
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {e}")
                progress.update(success=False)

    def _process_parallel(self, image_files: List[str], progress: ProgressTracker) -> None:
        """Process images in parallel"""
        max_workers = min(4, len(image_files))  # Limit to 4 workers to avoid overwhelming APIs
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image = {
                executor.submit(self.process_image, image_file, progress): image_file 
                for image_file in image_files
            }
            
            for future in as_completed(future_to_image):
                image_file = future_to_image[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Failed to process {image_file}: {e}")
                    progress.update(success=False, item_name=image_file, step="Error")

    def process_image(
        self, 
        image_file: str, 
        progress_tracker: Optional[ProgressTracker] = None
    ) -> bool:
        """
        Process a single image and return success status.
        
        Args:
            image_file: Path to image file
            progress_tracker: Optional progress tracker
            
        Returns:
            True if processing succeeded, False otherwise
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing image: {image_file}")
            
            # Update progress with current image
            if progress_tracker:
                progress_tracker.update_status(item_name=image_file, step="Starting")
            
            # Check for existing analysis in database first
            image_md5 = compute_file_hash(image_file, algorithm='md5')
            if not self.config.get('FORCE_REPROCESS', False):
                existing_db_result = self.db_manager.get_result_by_md5(image_md5)
                if existing_db_result:
                    logger.info(f"Skipping {image_file} - analysis already exists in database")
                    if progress_tracker:
                        progress_tracker.update_status(item_name=image_file, step="Skipped (exists)")
                    return True
            
            # Check for existing analysis in files
            existing_result = self._load_existing_analysis(image_file)
            if existing_result and not self.config.get('FORCE_REPROCESS', False):
                logger.info(f"Skipping {image_file} - analysis already exists in files")
                if progress_tracker:
                    progress_tracker.update_status(item_name=image_file, step="Skipped (exists)")
                return True
            
            # Create unified analysis result
            analysis_result = UnifiedAnalysisResult(image_file, self.config)
            
            # Process image metadata
            if self.config.get('ENABLE_METADATA_EXTRACTION', True):
                if progress_tracker:
                    progress_tracker.update_status(item_name=image_file, step="Metadata")
                try:
                    metadata = extract_metadata(image_file)
                    analysis_result.add_metadata(metadata)
                except Exception as e:
                    logger.warning(f"Failed to extract metadata for {image_file}: {e}")
            
            # CLIP Analysis
            if self.config['ENABLE_CLIP_ANALYSIS']:
                if progress_tracker:
                    progress_tracker.update_status(item_name=image_file, step="CLIP")
                try:
                    # Create progress callback for CLIP analysis
                    def clip_progress_callback(step="CLIP", mode=""):
                        if progress_tracker:
                            progress_tracker.update_status(item_name=image_file, step=step, mode=mode)
                    
                    clip_result = analyze_image_with_clip(
                        image_path=image_file,
                        api_base_url=self.config['API_BASE_URL'],
                        model=self.config['CLIP_MODEL_NAME'],
                        modes=self.config['CLIP_MODES'],
                        force_reprocess=self.config.get('FORCE_REPROCESS', False),
                        progress_callback=clip_progress_callback
                    )
                    analysis_result.add_clip_result(clip_result)
                except Exception as e:
                    logger.error(f"CLIP analysis failed for {image_file}: {e}")
                    analysis_result.mark_failed(f"CLIP analysis failed: {e}")
            
            # LLM Analysis
            if self.config['ENABLE_LLM_ANALYSIS']:
                if progress_tracker:
                    progress_tracker.update_status(item_name=image_file, step="LLM")
                
                configured_llm_models = self.db_manager.get_llm_models()
                
                if configured_llm_models:
                    llm_results = {}
                    for model_config in configured_llm_models:
                        if progress_tracker:
                            progress_tracker.update_status(
                                item_name=image_file, 
                                step="LLM", 
                                mode=model_config['name']
                            )
                        try:
                            llm_result = self.llm_manager.analyze_image(
                                image_path=image_file,
                                prompt="Describe this image in detail, including visual elements, style, composition, and any notable features.",
                                model_config=model_config
                            )
                            llm_results[model_config['name']] = llm_result
                        except Exception as e:
                            logger.error(f"LLM analysis failed for {image_file} with model {model_config['name']}: {e}")
                            llm_results[model_config['name']] = {
                                "status": "error",
                                "message": str(e),
                                "model": model_config['name'],
                                "provider": model_config['type']
                            }
                    
                    analysis_result.add_llm_results(llm_results)
                else:
                    logger.warning("No LLM models configured. Skipping LLM analysis.")
            
            # Mark as complete and save
            if progress_tracker:
                progress_tracker.update_status(item_name=image_file, step="Saving")
            processing_time = time.time() - start_time
            analysis_result.mark_complete(processing_time)
            output_path = analysis_result.save(self.config['OUTPUT_DIRECTORY'])
            
            # Save to database
            try:
                self.db_manager.insert_result(
                    filename=analysis_result.filename,
                    directory=analysis_result.directory,
                    md5=analysis_result.md5,
                    model=analysis_result.result.get("analysis", {}).get("clip", {}).get("model", "unknown"),
                    modes=json.dumps(self.config.get('CLIP_MODES', [])),
                    prompts=json.dumps(analysis_result.result.get("analysis", {}).get("clip", {}).get("prompt", {})),
                    analysis_results=json.dumps(analysis_result.result.get("analysis", {})),
                    settings=json.dumps(self.config),
                    llm_results=json.dumps(analysis_result.result.get("analysis", {}).get("llm", {}))
                )
                logger.info(f"Saved analysis to database for {image_file}")
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")
            
            if output_path:
                logger.info(f"[SUCCESS] Successfully processed {image_file} in {processing_time:.2f}s")
                if progress_tracker:
                    progress_tracker.update(success=True, item_name=image_file, step="Complete")
                return True
            else:
                logger.error(f"[ERROR] Failed to save results for {image_file}")
                if progress_tracker:
                    progress_tracker.update(success=False, item_name=image_file, step="Failed")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to process image {image_file}: {e}")
            if progress_tracker:
                progress_tracker.update(success=False, item_name=image_file, step="Error")
            return False

    def _load_existing_analysis(self, image_file: str) -> Optional[Dict[str, Any]]:
        """Load existing analysis if it exists"""
        base_filename = os.path.splitext(os.path.basename(image_file))[0]
        analysis_path = os.path.join(self.config['OUTPUT_DIRECTORY'], f"{base_filename}_analysis.json")
        
        if os.path.exists(analysis_path):
            try:
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                # Check if the image has changed (MD5 comparison)
                current_md5 = compute_file_hash(image_file, algorithm='md5')
                if existing_data.get('file_info', {}).get('md5') == current_md5:
                    return existing_data
                else:
                    logger.info(f"Image {image_file} has changed, will reprocess")
                    return None
            except Exception as e:
                logger.warning(f"Failed to load existing analysis for {image_file}: {e}")
                return None
        return None

    def _generate_summaries(self) -> None:
        """Generate summary files from all analysis results"""
        if not self.config.get('GENERATE_SUMMARIES', True):
            return
            
        print("\n📊 Generating summary files...")
        
        summary_dir = self.config['OUTPUT_DIRECTORY']
        analysis_files = [f for f in os.listdir(summary_dir) if f.endswith('_analysis.json')]
        
        if not analysis_files:
            print("No analysis files found to summarize")
            return
        
        # Load all analysis results
        all_results = []
        for analysis_file in analysis_files:
            try:
                with open(os.path.join(summary_dir, analysis_file), 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    all_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to load {analysis_file}: {e}")
        
        # Generate different types of summaries
        self._generate_clip_summary(all_results, summary_dir)
        self._generate_llm_summary(all_results, summary_dir)
        self._generate_metadata_summary(all_results, summary_dir)
        
        print(f"✅ Generated summary files in {summary_dir}")

    def _generate_clip_summary(self, results: List[Dict], summary_dir: str) -> None:
        """Generate CLIP analysis summary"""
        clip_results = []
        for result in results:
            if result.get('analysis', {}).get('clip'):
                clip_results.append({
                    'filename': result['file_info']['filename'],
                    'directory': result['file_info']['directory'],
                    'clip_analysis': result['analysis']['clip']
                })
        
        if clip_results:
            summary_path = os.path.join(summary_dir, 'clip_analysis_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(clip_results, f, indent=2, ensure_ascii=False)

    def _generate_llm_summary(self, results: List[Dict], summary_dir: str) -> None:
        """Generate LLM analysis summary"""
        llm_results = []
        for result in results:
            if result.get('analysis', {}).get('llm'):
                llm_results.append({
                    'filename': result['file_info']['filename'],
                    'directory': result['file_info']['directory'],
                    'llm_analysis': result['analysis']['llm']
                })
        
        if llm_results:
            summary_path = os.path.join(summary_dir, 'llm_analysis_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(llm_results, f, indent=2, ensure_ascii=False)

    def _generate_metadata_summary(self, results: List[Dict], summary_dir: str) -> None:
        """Generate metadata summary"""
        metadata_results = []
        for result in results:
            if result.get('analysis', {}).get('metadata'):
                metadata_results.append({
                    'filename': result['file_info']['filename'],
                    'directory': result['file_info']['directory'],
                    'metadata': result['analysis']['metadata']
                })
        
        if metadata_results:
            summary_path = os.path.join(summary_dir, 'metadata_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_results, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Main entry point with improved configuration loading"""
    print("🖼️  Image Analysis with CLIP and LLM")
    print("=" * 50)
    
    # Load configuration from environment variables
    config = {
        'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:7860'),
        'CLIP_MODEL_NAME': os.getenv('CLIP_MODEL_NAME', 'ViT-L-14/openai'),
        'ENABLE_CLIP_ANALYSIS': os.getenv('ENABLE_CLIP_ANALYSIS', 'True') == 'True',
        'ENABLE_LLM_ANALYSIS': os.getenv('ENABLE_LLM_ANALYSIS', 'True') == 'True',
        'ENABLE_PARALLEL_PROCESSING': os.getenv('ENABLE_PARALLEL_PROCESSING', 'False') == 'True',
        'ENABLE_METADATA_EXTRACTION': os.getenv('ENABLE_METADATA_EXTRACTION', 'True') == 'True',
        'IMAGE_DIRECTORY': os.getenv('IMAGE_DIRECTORY', 'Images'),
        'OUTPUT_DIRECTORY': os.getenv('OUTPUT_DIRECTORY', 'Output'),
        'CLIP_MODES': [mode.strip() for mode in os.getenv('CLIP_MODES', 'best,fast,classic,negative,caption').split(',')],
        'PROMPT_CHOICES': [p.strip() for p in os.getenv('PROMPT_CHOICES', 'P1,P2').split(',')],
        'DEBUG': os.getenv('DEBUG', 'False') == 'True',
        'FORCE_REPROCESS': os.getenv('FORCE_REPROCESS', 'False') == 'True',
        'GENERATE_SUMMARIES': os.getenv('GENERATE_SUMMARIES', 'True') == 'True'
    }

    try:
        processor = DirectoryProcessor(config)
        processor.process_directory()
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()