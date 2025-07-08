#!/usr/bin/env python3
"""
Image Analysis with CLIP and LLM - Main Entry Point
Supports both interactive and non-interactive CLI modes
"""

import os
import sys
import argparse
import subprocess
from typing import Dict, Any, List
from dotenv import load_dotenv

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Load environment variables
load_dotenv()

# Import after environment loading
from src.utils.logger import setup_global_logging, get_global_logger
from src.utils.error_handler import setup_global_error_handling, ErrorCategory, error_context
from src.utils.debug_utils import enable_debug_mode, disable_debug_mode, get_debug_info

# Setup global logging and error handling
logger = setup_global_logging()
error_handler = setup_global_error_handling(logger)

# Import after environment loading
from directory_processor import DirectoryProcessor
from src.viewers.web_interface_refactored import WebInterface
import src.config.config_manager as config_manager
from src.analyzers.llm_manager import LLMManager
from src.database.db_manager import DatabaseManager

def get_default_config() -> Dict[str, Any]:
    """Get default configuration with environment variable fallbacks"""
    return {
        'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:7860'),
        'CLIP_MODEL_NAME': os.getenv('CLIP_MODEL_NAME', 'ViT-L-14/openai'),
        'ENABLE_CLIP_ANALYSIS': os.getenv('ENABLE_CLIP_ANALYSIS', 'True') == 'True',
        'ENABLE_LLM_ANALYSIS': os.getenv('ENABLE_LLM_ANALYSIS', 'True') == 'True',
        'ENABLE_METADATA_EXTRACTION': os.getenv('ENABLE_METADATA_EXTRACTION', 'True') == 'True',
        'ENABLE_PARALLEL_PROCESSING': os.getenv('ENABLE_PARALLEL_PROCESSING', 'False') == 'True',
        'FORCE_REPROCESS': os.getenv('FORCE_REPROCESS', 'False') == 'True',
        'GENERATE_SUMMARIES': os.getenv('GENERATE_SUMMARIES', 'True') == 'True',
        'DEBUG': os.getenv('DEBUG', 'False') == 'True',
        'IMAGE_DIRECTORY': os.getenv('IMAGE_DIRECTORY', 'Images'),
        'OUTPUT_DIRECTORY': os.getenv('OUTPUT_DIRECTORY', 'Output'),
        'WEB_PORT': int(os.getenv('WEB_PORT', '5050')),
        'CLIP_MODES': os.getenv('CLIP_MODES', 'best,fast,classic,negative,caption').split(','),
        'PROMPT_CHOICES': os.getenv('PROMPT_CHOICES', 'P1,P2').split(','),
        'OLLAMA_URL': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'OPENAI_URL': os.getenv('OPENAI_URL', 'https://api.openai.com/v1'),
    }

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with all available options"""
    parser = argparse.ArgumentParser(
        description="Image Analysis with CLIP and LLM - Comprehensive CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (no arguments)
  python main.py

  # Non-interactive mode with all options
  python main.py process --no-interactive --input Images --output Results --clip-modes best,fast --enable-llm --api-url http://localhost:7860 --clip-model ViT-L-14/openai

  # Process with custom settings
  python main.py process --input Images --output Results --clip-modes best,fast --enable-llm

  # Start web interface
  python main.py web --port 8080 --host 0.0.0.0 --debug

  # Configure LLM models non-interactively
  python main.py llm-config --no-interactive --add-ollama llama2 --add-openai gpt-4 --openai-key your_key_here

  # View results
  python main.py view --list
  python main.py view --file Output/image_analysis.json

  # Get help for specific command
  python main.py process --help
  python main.py llm-config --help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Helper function to add global flags to subcommands
    def add_global_flags(subparser):
        subparser.add_argument('--no-interactive', action='store_true', 
                              help='Run in non-interactive mode (no prompts, exit on missing required args)')
        subparser.add_argument('--yes', '-y', action='store_true',
                              help='Automatically answer yes to all prompts')
        subparser.add_argument('--verbose', '-v', action='store_true',
                              help='Enable verbose output')
        subparser.add_argument('--quiet', '-q', action='store_true',
                              help='Suppress output (except errors)')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process images for analysis')
    add_global_flags(process_parser)
    process_parser.add_argument('--input', '-i', default='Images', help='Input directory (default: Images)')
    process_parser.add_argument('--output', '-o', default='Output', help='Output directory (default: Output)')
    process_parser.add_argument('--api-url', default='http://localhost:7860', help='CLIP API URL')
    process_parser.add_argument('--clip-model', default='ViT-L-14/openai', help='CLIP model name')
    process_parser.add_argument('--clip-modes', nargs='+', default=['best', 'fast'], help='CLIP analysis modes')
    process_parser.add_argument('--prompt-choices', nargs='+', default=['P1', 'P2'], help='Prompt choices for analysis')
    process_parser.add_argument('--enable-clip', action='store_true', default=True, help='Enable CLIP analysis')
    process_parser.add_argument('--disable-clip', action='store_true', help='Disable CLIP analysis')
    process_parser.add_argument('--enable-llm', action='store_true', default=True, help='Enable LLM analysis')
    process_parser.add_argument('--disable-llm', action='store_true', help='Disable LLM analysis')
    process_parser.add_argument('--enable-metadata', action='store_true', default=True, help='Enable metadata extraction')
    process_parser.add_argument('--disable-metadata', action='store_true', help='Disable metadata extraction')
    process_parser.add_argument('--enable-parallel', action='store_true', help='Enable parallel processing')
    process_parser.add_argument('--disable-parallel', action='store_true', help='Disable parallel processing')
    process_parser.add_argument('--enable-summaries', action='store_true', default=True, help='Enable summary generation')
    process_parser.add_argument('--disable-summaries', action='store_true', help='Disable summary generation')
    process_parser.add_argument('--force', action='store_true', help='Force reprocessing of existing results')
    process_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    process_parser.add_argument('--timeout', type=int, default=120, help='Timeout for API calls (seconds)')
    process_parser.add_argument('--retry-limit', type=int, default=3, help='Number of retries for failed API calls')
    process_parser.add_argument('--max-file-size', type=str, default='50MB', help='Maximum file size to process')
    process_parser.add_argument('--allowed-extensions', nargs='+', 
                               default=['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'], 
                               help='Allowed image file extensions')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    add_global_flags(web_parser)
    web_parser.add_argument('--port', '-p', type=int, default=5050, help='Port number (default: 5050)')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host address (default: 0.0.0.0)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    add_global_flags(config_parser)
    config_parser.add_argument('--interactive', '-i', action='store_true', help='Interactive configuration')
    config_parser.add_argument('--show', '-s', action='store_true', help='Show current configuration')
    config_parser.add_argument('--reset', '-r', action='store_true', help='Reset to defaults')
    config_parser.add_argument('--setup', action='store_true', help='Setup initial configuration files')
    config_parser.add_argument('--validate', action='store_true', help='Validate current configuration')
    config_parser.add_argument('--env-file', help='Path to .env file')
    config_parser.add_argument('--config-file', help='Path to config.json file')
    
    # LLM Config command
    llm_parser = subparsers.add_parser('llm-config', help='LLM model configuration')
    add_global_flags(llm_parser)
    llm_parser.add_argument('--list', '-l', action='store_true', help='List available models')
    llm_parser.add_argument('--list-configured', action='store_true', help='List configured models')
    llm_parser.add_argument('--add-ollama', help='Add Ollama model (e.g., llama2)')
    llm_parser.add_argument('--add-openai', help='Add OpenAI model (e.g., gpt-4)')
    llm_parser.add_argument('--add-anthropic', help='Add Anthropic model (e.g., claude-3-sonnet)')
    llm_parser.add_argument('--add-google', help='Add Google model (e.g., gemini-pro)')
    llm_parser.add_argument('--remove', type=int, help='Remove model by ID')
    llm_parser.add_argument('--enable', type=int, help='Enable model by ID')
    llm_parser.add_argument('--disable', type=int, help='Disable model by ID')
    llm_parser.add_argument('--test-ollama', action='store_true', help='Test Ollama connection')
    llm_parser.add_argument('--test-openai', action='store_true', help='Test OpenAI connection')
    llm_parser.add_argument('--test-anthropic', action='store_true', help='Test Anthropic connection')
    llm_parser.add_argument('--test-google', action='store_true', help='Test Google connection')
    llm_parser.add_argument('--test-all', action='store_true', help='Test all connections')
    llm_parser.add_argument('--ollama-url', default='http://localhost:11434', help='Ollama server URL')
    llm_parser.add_argument('--openai-key', help='OpenAI API key')
    llm_parser.add_argument('--anthropic-key', help='Anthropic API key')
    llm_parser.add_argument('--google-key', help='Google API key')
    llm_parser.add_argument('--openai-url', default='https://api.openai.com/v1', help='OpenAI API URL')
    llm_parser.add_argument('--anthropic-url', default='https://api.anthropic.com', help='Anthropic API URL')
    llm_parser.add_argument('--google-url', default='https://generativelanguage.googleapis.com', help='Google API URL')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View analysis results')
    add_global_flags(view_parser)
    view_parser.add_argument('--list', '-l', action='store_true', help='List all results')
    view_parser.add_argument('--file', '-f', help='View specific result file')
    view_parser.add_argument('--summary', '-s', action='store_true', help='Generate summary')
    view_parser.add_argument('--export', choices=['csv', 'json'], help='Export format')
    view_parser.add_argument('--output', '-o', help='Export output file')
    
    # Database command
    db_parser = subparsers.add_parser('database', help='Database management')
    add_global_flags(db_parser)
    db_parser.add_argument('--stats', '-s', action='store_true', help='Show database statistics')
    db_parser.add_argument('--clear', '-c', action='store_true', help='Clear all results')
    db_parser.add_argument('--backup', '-b', help='Backup database to file')
    db_parser.add_argument('--restore', '-r', help='Restore database from file')
    
    # Wildcard command
    wildcard_parser = subparsers.add_parser('wildcard', help='Generate wildcard files from analysis results')
    add_global_flags(wildcard_parser)
    wildcard_parser.add_argument('--output', '-o', default='Output', help='Output directory (default: Output)')
    wildcard_parser.add_argument('--groups', '-g', action='store_true', help='Generate individual group wildcards')
    wildcard_parser.add_argument('--combined', '-c', action='store_true', help='Generate combined wildcard')
    wildcard_parser.add_argument('--combinations', action='store_true', help='Generate group combinations')
    wildcard_parser.add_argument('--all', '-a', action='store_true', help='Generate all wildcard types')
    
    return parser

def handle_process(args: argparse.Namespace) -> int:
    """Handle process command"""
    logger.info('Starting process command with args', data={'args': str(args)})
    if not getattr(args, 'quiet', False):
        print("[IMAGE] Starting Image Analysis...")
    
    # Build configuration from arguments
    config = get_default_config()
    
    # Override with command line arguments
    config['IMAGE_DIRECTORY'] = args.input
    config['OUTPUT_DIRECTORY'] = args.output
    config['API_BASE_URL'] = args.api_url
    config['CLIP_MODEL_NAME'] = args.clip_model
    config['CLIP_MODES'] = args.clip_modes
    config['PROMPT_CHOICES'] = args.prompt_choices
    config['ENABLE_CLIP_ANALYSIS'] = args.enable_clip and not args.disable_clip
    config['ENABLE_LLM_ANALYSIS'] = args.enable_llm and not args.disable_llm
    config['ENABLE_METADATA_EXTRACTION'] = args.enable_metadata and not args.disable_metadata
    config['ENABLE_PARALLEL_PROCESSING'] = args.enable_parallel and not args.disable_parallel
    config['GENERATE_SUMMARIES'] = args.enable_summaries and not args.disable_summaries
    config['FORCE_REPROCESS'] = args.force
    config['DEBUG'] = args.debug
    config['TIMEOUT'] = args.timeout
    config['RETRY_LIMIT'] = args.retry_limit
    config['MAX_FILE_SIZE'] = args.max_file_size
    config['ALLOWED_EXTENSIONS'] = args.allowed_extensions
    
    # Validate required settings in non-interactive mode
    if args.no_interactive:
        if not os.path.exists(config['IMAGE_DIRECTORY']):
            print(f"❌ Input directory does not exist: {config['IMAGE_DIRECTORY']}")
            return 1
        
        if not config['ENABLE_CLIP_ANALYSIS'] and not config['ENABLE_LLM_ANALYSIS']:
            print("❌ At least one analysis type must be enabled (CLIP or LLM)")
            return 1
    
    # Create directories if they don't exist
    os.makedirs(config['IMAGE_DIRECTORY'], exist_ok=True)
    os.makedirs(config['OUTPUT_DIRECTORY'], exist_ok=True)
    
    if args.verbose:
        print(f"[DIR] Input directory: {config['IMAGE_DIRECTORY']}")
        print(f"[DIR] Output directory: {config['OUTPUT_DIRECTORY']}")
        print(f"[API] API URL: {config['API_BASE_URL']}")
        print(f"[LLM] CLIP Model: {config['CLIP_MODEL_NAME']}")
        print(f"[TARGET] CLIP Modes: {config['CLIP_MODES']}")
        print(f"[PROMPT] Prompt Choices: {config['PROMPT_CHOICES']}")
        print(f"[CLIP] CLIP Analysis: {'[ENABLED]' if config['ENABLE_CLIP_ANALYSIS'] else '[DISABLED]'}")
        print(f"[LLM] LLM Analysis: {'[ENABLED]' if config['ENABLE_LLM_ANALYSIS'] else '[DISABLED]'}")
        print(f"[META] Metadata Extraction: {'[ENABLED]' if config['ENABLE_METADATA_EXTRACTION'] else '[DISABLED]'}")
        print(f"[PARALLEL] Parallel Processing: {'[ENABLED]' if config['ENABLE_PARALLEL_PROCESSING'] else '[DISABLED]'}")
        print(f"[SUMMARY] Generate Summaries: {'[ENABLED]' if config['GENERATE_SUMMARIES'] else '[DISABLED]'}")
        print(f"[FORCE] Force Reprocess: {'[ENABLED]' if config['FORCE_REPROCESS'] else '[DISABLED]'}")
        print(f"[DEBUG] Debug Mode: {'[ENABLED]' if config['DEBUG'] else '[DISABLED]'}")
    
    try:
        processor = DirectoryProcessor(config)
        processor.process_directory()
        logger.info('Processing completed successfully!')
        if not getattr(args, 'quiet', False):
            print("[SUCCESS] Processing completed successfully!")
        return 0
    except Exception as e:
        logger.error('Processing failed', data={'error': str(e)}, exc_info=True)
        print(f"[ERROR] Processing failed: {e}")
        if getattr(args, 'debug', False):
            import traceback
            traceback.print_exc()
        return 1

def handle_web(args: argparse.Namespace) -> int:
    """Handle web command"""
    print(f"[WEB] Starting Web Interface on {args.host}:{args.port}")
    
    try:
        web_interface = WebInterface()
        web_interface.run(host=args.host, port=args.port, debug=args.debug)
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to start web interface: {e}")
        return 1

def handle_config(args: argparse.Namespace) -> int:
    """Handle config command"""
    if args.show:
        print("[CONFIG] Current Configuration:")
        # Show current environment variables
        config = get_default_config()
        for key, value in config.items():
            print(f"  {key}: {value}")
        return 0
    elif args.reset:
        print("[RESET] Resetting configuration to defaults...")
        try:
            from src.config.config_manager import create_default_env_file
            if create_default_env_file():
                print("[SUCCESS] Configuration reset complete!")
                return 0
            else:
                print("[ERROR] Failed to reset configuration")
                return 1
        except Exception as e:
            print(f"[ERROR] Error resetting configuration: {e}")
            return 1
    elif args.validate:
        print("[CONFIG] Validating configuration...")
        from src.config.config_manager import validate_config
        issues = validate_config()
        if issues["errors"]:
            print("❌ Configuration Errors:")
            for error in issues["errors"]:
                print(f"  • {error}")
        if issues["warnings"]:
            print("⚠️  Configuration Warnings:")
            for warning in issues["warnings"]:
                print(f"  • {warning}")
        if not issues["errors"] and not issues["warnings"]:
            print("🎉 Configuration is valid and ready to use!")
            return 0
        else:
            return 1
    else:
        print("[CONFIG] Interactive Configuration")
        print("Interactive config mode is not implemented in this version.")
        return 0

def handle_llm_config(args: argparse.Namespace) -> int:
    """Handle LLM configuration"""
    llm_manager = LLMManager()
    db_manager = DatabaseManager()
    
    if args.list:
        print("[LLM] Available Models:")
        models = llm_manager.get_all_available_models()
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model['name']} ({model['type']})")
            if model.get('size'):
                print(f"     Size: {model['size']}")
        return 0
    
    elif args.list_configured:
        print("[CONFIG] Configured Models:")
        models = db_manager.get_llm_models()
        if models:
            for model in models:
                print(f"  ID {model['id']}: {model['name']} ({model['type']})")
        else:
            print("  No models configured")
        return 0
    
    elif args.add_ollama:
        print(f"[ADD] Adding Ollama model: {args.add_ollama}")
        db_manager.insert_llm_model(
            name=args.add_ollama,
            type='ollama',
            url=args.ollama_url,
            model_name=args.add_ollama
        )
        print("[SUCCESS] Ollama model added successfully!")
        return 0
    
    elif args.add_openai:
        if not args.openai_key:
            print("[ERROR] OpenAI API key required. Use --openai-key")
            return 1
        
        print(f"[ADD] Adding OpenAI model: {args.add_openai}")
        db_manager.insert_llm_model(
            name=args.add_openai,
            type='openai',
            url='https://api.openai.com/v1',
            api_key=args.openai_key,
            model_name=args.add_openai
        )
        print("[SUCCESS] OpenAI model added successfully!")
        return 0
    
    elif args.remove:
        print(f"[DELETE] Removing model ID: {args.remove}")
        if db_manager.delete_llm_model(args.remove):
            print("[SUCCESS] Model removed successfully!")
        else:
            print("[ERROR] Failed to remove model")
            return 1
        return 0
    
    elif args.test_ollama:
        print("[TEST] Testing Ollama connection...")
        if llm_manager.test_ollama_connection():
            print("[SUCCESS] Ollama connection successful!")
        else:
            print("[ERROR] Ollama connection failed")
            return 1
        return 0
    
    elif args.test_openai:
        print("[TEST] Testing OpenAI connection...")
        if llm_manager.test_openai_connection():
            print("[SUCCESS] OpenAI connection successful!")
        else:
            print("[ERROR] OpenAI connection failed")
            return 1
        return 0
    
    else:
        print("[LLM] LLM Configuration")
        print("Use --help for available options")
        return 0

def handle_view(args: argparse.Namespace) -> int:
    """Handle view command"""
    db_manager = DatabaseManager()
    
    if args.list:
        print("[RESULTS] Analysis Results:")
        results = db_manager.get_all_results()
        for result in results:
            print(f"  ID {result['id']}: {result['filename']} ({result['date_added']})")
        return 0
    
    elif args.file:
        print(f"[FILE] Viewing file: {args.file}")
        # Implementation for viewing specific file
        print("File viewing not yet implemented")
        return 0
    
    elif args.summary:
        print("[STATS] Database Statistics:")
        stats = db_manager.get_stats()
        print(f"  Total results: {stats['total_results']}")
        print(f"  Recent results: {stats['recent_results']}")
        print(f"  LLM models: {stats['llm_models']}")
        return 0
    
    else:
        print("📋 View Analysis Results")
        print("Use --help for available options")
        return 0

def handle_database(args: argparse.Namespace) -> int:
    """Handle database command"""
    db_manager = DatabaseManager()
    
    if args.stats:
        print("📊 Database Statistics:")
        stats = db_manager.get_stats()
        print(f"  Total results: {stats['total_results']}")
        print(f"  Recent results: {stats['recent_results']}")
        print(f"  LLM models: {stats['llm_models']}")
        return 0
    
    elif args.clear:
        print("🗑️  Clearing all database results...")
        if db_manager.clear_database():
            print("✅ Database cleared successfully!")
        else:
            print("❌ Failed to clear database")
            return 1
        return 0
    
    else:
        print("🗄️  Database Management")
        print("Use --help for available options")
        return 0

def handle_wildcard(args: argparse.Namespace) -> int:
    """Handle wildcard command"""
    try:
        from src.utils.wildcard_generator import WildcardGenerator
        
        print("🎲 Generating Wildcard Files...")
        
        # Initialize wildcard generator
        generator = WildcardGenerator(args.output)
        db_manager = DatabaseManager()
        
        # Get all results from database
        results = db_manager.get_all_results()
        
        if not results:
            print("❌ No analysis results found in database")
            print("Please run analysis first with: python main.py process")
            return 1
        
        print(f"📊 Found {len(results)} analysis results")
        
        # Determine base directory from results
        base_directory = results[0].get('directory', 'Images')
        
        generated_files = {}
        
        # Generate individual group wildcards
        if args.groups or args.all:
            print("📁 Generating individual group wildcards...")
            group_files = generator.generate_wildcards_from_results(results, base_directory)
            generated_files.update(group_files)
            print(f"✅ Generated {len(group_files)} group wildcard files")
        
        # Generate combined wildcard
        if args.combined or args.all:
            print("🔗 Generating combined wildcard...")
            combined_file = generator.generate_combined_wildcard(results, base_directory)
            if combined_file:
                generated_files['combined'] = combined_file
                print(f"✅ Generated combined wildcard: {combined_file}")
        
        # Generate group combinations
        if args.combinations or args.all:
            print("🔄 Generating group combinations...")
            combo_files = generator.generate_group_combinations(results, base_directory)
            generated_files.update(combo_files)
            print(f"✅ Generated {len(combo_files)} combination wildcard files")
        
        # Show summary
        if generated_files:
            print("\n📋 Generated Wildcard Files:")
            for name, path in generated_files.items():
                print(f"  {name}: {path}")
            
            print(f"\n🎉 Successfully generated {len(generated_files)} wildcard files!")
            print(f"📂 Files saved in: {generator.wildcards_dir}")
            return 0
        else:
            print("❌ No wildcard files were generated")
            return 1
            
    except ImportError as e:
        print(f"❌ Failed to import wildcard generator: {e}")
        return 1
    except Exception as e:
        print(f"❌ Failed to generate wildcards: {e}")
        return 1

def show_help():
    """Show detailed help information"""
    print("🖼️  Image Analysis with CLIP and LLM - Help")
    print("=" * 60)
    print()
    print("This tool analyzes images using CLIP and LLM models.")
    print()
    print("Available Commands:")
    print("  process     - Process images for analysis")
    print("  web         - Start web interface")
    print("  config      - Configuration management")
    print("  llm-config  - LLM model configuration")
    print("  view        - View analysis results")
    print("  database    - Database management")
    print()
    print("Examples:")
    print("  python main.py process --input Images --output Results")
    print("  python main.py web --port 5050")
    print("  python main.py llm-config --list")
    print()
    print("For detailed help on any command:")
    print("  python main.py <command> --help")

def interactive_mode():
    """Run interactive mode when no arguments provided"""
    print("🖼️  Image Analysis with CLIP and LLM")
    print("=" * 50)
    print()
    
    while True:
        print("Available commands:")
        print("  1. process  - Process images for analysis")
        print("  2. web      - Start web interface")
        print("  3. config   - Configuration management")
        print("  4. llm-config - LLM model configuration")
        print("  5. view     - View analysis results")
        print("  6. database - Database management")
        print("  7. help     - Show detailed help")
        print("  8. exit     - Exit program")
        print()
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            print("\n🖼️  Image Processing")
            print("Press Enter to use defaults, or specify options:")
            input_dir = input("Input directory (default: Images): ").strip() or "Images"
            output_dir = input("Output directory (default: Output): ").strip() or "Output"
            
            config = get_default_config()
            config['IMAGE_DIRECTORY'] = input_dir
            config['OUTPUT_DIRECTORY'] = output_dir
            
            try:
                processor = DirectoryProcessor(config)
                processor.process_directory()
                print("✅ Processing completed!")
            except Exception as e:
                print(f"❌ Processing failed: {e}")
        
        elif choice == '2':
            print("\n🌐 Starting Web Interface...")
            try:
                app.run(host='0.0.0.0', port=5050, debug=False)
            except KeyboardInterrupt:
                print("\nWeb interface stopped")
            except Exception as e:
                print(f"❌ Failed to start web interface: {e}")
        
        elif choice == '3':
            print("\n⚙️  Configuration")
            config_manager.main()
        
        elif choice == '4':
            print("\n🤖 LLM Configuration")
            print("Available options:")
            print("  - List available models")
            print("  - Add/remove models")
            print("  - Test connections")
            print("Use 'python main.py llm-config --help' for details")
        
        elif choice == '5':
            print("\n📋 View Results")
            db_manager = DatabaseManager()
            stats = db_manager.get_stats()
            print(f"Total results: {stats['total_results']}")
            print("Use 'python main.py view --help' for details")
        
        elif choice == '6':
            print("\n🗄️  Database Management")
            print("Use 'python main.py database --help' for details")
        
        elif choice == '7':
            print("\n📖 Help")
            subprocess.run([sys.executable, __file__, '--help'])
        
        elif choice == '8':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-8.")
        
        print()

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle global flags
    if hasattr(args, 'quiet') and args.quiet:
        # Suppress all output except errors
        import sys
        sys.stdout = open(os.devnull, 'w')
    
    # If no command provided, run interactive mode (unless --no-interactive is set)
    if not args.command:
        if hasattr(args, 'no_interactive') and args.no_interactive:
            print("❌ No command specified and --no-interactive mode is enabled")
            print("Please specify a command. Use --help for available options.")
            return 1
        interactive_mode()
        return 0
    
    # Handle specific commands
    try:
        if args.command == 'process':
            return handle_process(args)
        elif args.command == 'web':
            return handle_web(args)
        elif args.command == 'config':
            return handle_config(args)
        elif args.command == 'llm-config':
            return handle_llm_config(args)
        elif args.command == 'view':
            return handle_view(args)
        elif args.command == 'database':
            return handle_database(args)
        elif args.command == 'wildcard':
            return handle_wildcard(args)
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        if not (hasattr(args, 'quiet') and args.quiet):
            print("\n👋 Operation cancelled by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main()) 