import os
import json
import logging
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from src.analyzers.clip_analyzer import analyze_image_with_clip
from src.analyzers.llm_analyzer import analyze_image_with_llm, MODELS
from src.analyzers.metadata_extractor import extract_metadata
import requests
from datetime import datetime
from pathlib import Path
import sys

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("processing.log", encoding='utf-8')
    ]
)

class ProgressTracker:
    """Tracks and displays progress for batch processing"""
    
    def __init__(self, total_items: int):
        self.total_items = total_items
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        
    def update(self, success: bool = True):
        self.completed += 1
        if not success:
            self.failed += 1
        self._display_progress()
    
    def _display_progress(self):
        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed if elapsed > 0 else 0
        eta = (self.total_items - self.completed) / rate if rate > 0 else 0
        
        progress_bar = self._create_progress_bar()
        
        print(f"\r{progress_bar} {self.completed}/{self.total_items} "
              f"({self.completed/self.total_items*100:.1f}%) "
              f"| Failed: {self.failed} | "
              f"Rate: {rate:.1f}/s | ETA: {eta:.0f}s", end="", flush=True)
    
    def _create_progress_bar(self, width: int = 30) -> str:
        filled = int(width * self.completed / self.total_items)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def finish(self):
        elapsed = time.time() - self.start_time
        print(f"\n✅ Processing complete! "
              f"Processed {self.completed} images in {elapsed:.1f}s "
              f"({self.completed/elapsed:.1f} images/s)")
        if self.failed > 0:
            print(f"❌ {self.failed} images failed to process")

class UnifiedAnalysisResult:
    """Represents a unified analysis result for a single image"""
    
    def __init__(self, image_path: str, config: Dict[str, Any]):
        self.image_path = image_path
        self.config = config
        self.filename = os.path.basename(image_path)
        self.directory = os.path.dirname(image_path).replace("\\", "/")
        self.md5 = self._compute_md5()
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
    
    def _compute_md5(self) -> str:
        """Compute MD5 hash of the image file"""
        hash_md5 = hashlib.md5()
        try:
            with open(self.image_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Failed to compute MD5 for {self.image_path}: {e}")
            return "unknown"
    
    def add_clip_result(self, clip_result: Dict[str, Any]):
        """Add CLIP analysis results"""
        if clip_result.get("status") == "success":
            self.result["analysis"]["clip"] = clip_result.get("prompt", {})
        else:
            self.result["processing_info"]["errors"].append({
                "type": "clip",
                "error": clip_result.get("message", "Unknown CLIP error")
            })
    
    def add_llm_result(self, llm_result: Dict[str, Any]):
        """Add LLM analysis results"""
        if llm_result.get("status") == "success":
            self.result["analysis"]["llm"] = llm_result.get("api_responses", {})
        else:
            self.result["processing_info"]["errors"].append({
                "type": "llm",
                "error": llm_result.get("message", "Unknown LLM error")
            })
    
    def add_metadata(self, metadata: Dict[str, Any]):
        """Add image metadata"""
        self.result["analysis"]["metadata"] = metadata
    
    def mark_complete(self, processing_time: float):
        """Mark analysis as complete"""
        self.result["processing_info"]["processing_time"] = processing_time
        self.result["processing_info"]["status"] = "complete"
        self.result["file_info"]["date_processed"] = datetime.now().isoformat()
    
    def mark_failed(self, error: str):
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
            logging.info(f"Saved unified analysis result to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Failed to save analysis result: {e}")
            return ""

class DirectoryProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_models = self.setup_llm_models() if self.config['ENABLE_LLM_ANALYSIS'] else []
        self.config['llm_models'] = self.llm_models  # Add to config for reference
        
        # Validate configuration
        self._validate_config()
        
        logging.info("DirectoryProcessor initialized with config: %s", self.config)
        logging.debug(f"CLIP Analysis Enabled: {self.config['ENABLE_CLIP_ANALYSIS']}")
        logging.debug(f"LLM Analysis Enabled: {self.config['ENABLE_LLM_ANALYSIS']}")
        logging.debug(f"Available LLM Models: {[m['title'] for m in self.llm_models]}")

    def _validate_config(self):
        """Validate configuration and provide helpful error messages"""
        errors = []
        
        if not os.path.exists(self.config['IMAGE_DIRECTORY']):
            errors.append(f"Image directory '{self.config['IMAGE_DIRECTORY']}' does not exist")
        
        if not os.path.exists(self.config['OUTPUT_DIRECTORY']):
            try:
                os.makedirs(self.config['OUTPUT_DIRECTORY'])
                logging.info(f"Created output directory: {self.config['OUTPUT_DIRECTORY']}")
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

    def setup_llm_models(self) -> List[Dict[str, Any]]:
        """Setup LLM models from configuration"""
        analyzers = []
        for model in MODELS:
            enabled = os.getenv(f"ENABLE_LLM_{model['number']}", 'False').lower() == 'true'
            if enabled:
                # Validate model configuration
                if not model.get('api_key'):
                    logging.warning(f"Model {model['title']} enabled but no API key provided")
                analyzers.append(model)
                logging.info(f"✅ {model['title']} is enabled for analysis")
            else:
                logging.debug(f"❌ {model['title']} is disabled for analysis")
        return analyzers

    def process_directory(self):
        """Process all images in the directory with progress tracking"""
        image_files = self.find_image_files(self.config['IMAGE_DIRECTORY'])
        
        if not image_files:
            print(f"❌ No image files found in {self.config['IMAGE_DIRECTORY']}")
            return
        
        print(f"🚀 Starting analysis of {len(image_files)} images...")
        print(f"📁 Input directory: {self.config['IMAGE_DIRECTORY']}")
        print(f"📁 Output directory: {self.config['OUTPUT_DIRECTORY']}")
        print(f"🔍 CLIP Analysis: {'✅ Enabled' if self.config['ENABLE_CLIP_ANALYSIS'] else '❌ Disabled'}")
        print(f"🤖 LLM Analysis: {'✅ Enabled' if self.config['ENABLE_LLM_ANALYSIS'] else '❌ Disabled'}")
        print()

        progress = ProgressTracker(len(image_files))
        
        if self.config['ENABLE_PARALLEL_PROCESSING']:
            self._process_parallel(image_files, progress)
        else:
            self._process_sequential(image_files, progress)
        
        progress.finish()
        self._generate_summaries()

    def _process_sequential(self, image_files: List[str], progress: ProgressTracker):
        """Process images sequentially"""
        for image_file in image_files:
            try:
                success = self.process_image(image_file)
                progress.update(success)
            except Exception as e:
                logging.error(f"Failed to process {image_file}: {e}")
                progress.update(False)

    def _process_parallel(self, image_files: List[str], progress: ProgressTracker):
        """Process images in parallel"""
        max_workers = min(4, len(image_files))  # Limit to 4 workers to avoid overwhelming APIs
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image = {
                executor.submit(self.process_image, image_file): image_file 
                for image_file in image_files
            }
            
            for future in as_completed(future_to_image):
                image_file = future_to_image[future]
                try:
                    success = future.result()
                    progress.update(success)
                except Exception as e:
                    logging.error(f"Failed to process {image_file}: {e}")
                    progress.update(False)

    def find_image_files(self, directory: str) -> List[str]:
        """Find all image files in directory and subdirectories"""
        image_files = []
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(supported_formats):
                    full_path = os.path.join(root, file)
                    image_files.append(full_path)
                    logging.debug(f"Found image file: {full_path}")
        
        return sorted(image_files)

    def process_image(self, image_file: str) -> bool:
        """Process a single image and return success status"""
        start_time = time.time()
        
        try:
            logging.info(f"Processing image: {image_file}")
            
            # Check for existing analysis
            existing_result = self._load_existing_analysis(image_file)
            if existing_result and not self.config.get('FORCE_REPROCESS', False):
                logging.info(f"Skipping {image_file} - analysis already exists")
                return True
            
            # Create unified analysis result
            analysis_result = UnifiedAnalysisResult(image_file, self.config)
            
            # Process image metadata
            if self.config.get('ENABLE_METADATA_EXTRACTION', True):
                try:
                    metadata = extract_metadata(image_file)
                    analysis_result.add_metadata(metadata)
                except Exception as e:
                    logging.warning(f"Failed to extract metadata for {image_file}: {e}")
            
            # CLIP Analysis
            if self.config['ENABLE_CLIP_ANALYSIS']:
                try:
                    clip_result = analyze_image_with_clip(
                        image_path=image_file,
                        api_base_url=self.config['API_BASE_URL'],
                        model=self.config['CLIP_MODEL_NAME'],
                        modes=self.config['CLIP_MODES']
                    )
                    analysis_result.add_clip_result(clip_result)
                except Exception as e:
                    logging.error(f"CLIP analysis failed for {image_file}: {e}")
                    analysis_result.mark_failed(f"CLIP analysis failed: {e}")
            
            # LLM Analysis
            if self.config['ENABLE_LLM_ANALYSIS']:
                for model_config in self.llm_models:
                    try:
                        llm_result = analyze_image_with_llm(
                            image_path_or_directory=image_file,
                            prompt_ids=self.config['PROMPT_CHOICES'],
                            model_number=model_config['number'],
                            debug=self.config['DEBUG']
                        )
                        analysis_result.add_llm_result(llm_result)
                    except Exception as e:
                        logging.error(f"LLM analysis failed for {image_file} with model {model_config['title']}: {e}")
                        analysis_result.mark_failed(f"LLM analysis failed with {model_config['title']}: {e}")
            
            # Mark as complete and save
            processing_time = time.time() - start_time
            analysis_result.mark_complete(processing_time)
            output_path = analysis_result.save(self.config['OUTPUT_DIRECTORY'])
            
            if output_path:
                logging.info(f"✅ Successfully processed {image_file} in {processing_time:.2f}s")
                return True
            else:
                logging.error(f"❌ Failed to save results for {image_file}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to process image {image_file}: {e}")
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
                current_md5 = UnifiedAnalysisResult(image_file, self.config).md5
                if existing_data.get('file_info', {}).get('md5') == current_md5:
                    return existing_data
                else:
                    logging.info(f"Image {image_file} has changed, will reprocess")
                    return None
            except Exception as e:
                logging.warning(f"Failed to load existing analysis for {image_file}: {e}")
                return None
        return None

    def _generate_summaries(self):
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
                logging.warning(f"Failed to load {analysis_file}: {e}")
        
        # Generate different types of summaries
        self._generate_clip_summary(all_results, summary_dir)
        self._generate_llm_summary(all_results, summary_dir)
        self._generate_metadata_summary(all_results, summary_dir)
        
        print(f"✅ Generated summary files in {summary_dir}")

    def _generate_clip_summary(self, results: List[Dict], summary_dir: str):
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

    def _generate_llm_summary(self, results: List[Dict], summary_dir: str):
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

    def _generate_metadata_summary(self, results: List[Dict], summary_dir: str):
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

def main():
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
        'CLIP_MODES': [mode.strip() for mode in os.getenv('CLIP_MODES', 'best,fast').split(',')],
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
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
