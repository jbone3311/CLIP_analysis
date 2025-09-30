# Image Analysis with CLIP and LLM

A comprehensive image analysis system that combines CLIP (Contrastive Language-Image Pre-training) and LLM (Large Language Model) technologies to provide detailed analysis of images. This system processes images in batches, generates descriptive captions, and creates prompt lists for various AI applications.

## ✨ Key Features

- **🔍 CLIP Analysis**: Multi-mode image analysis using CLIP interrogator
- **🤖 Multi-LLM Analysis**: Support for multiple LLM providers (Ollama, OpenAI, ChatGPT)
- **🔧 Dynamic Model Discovery**: Automatically discover available Ollama models
- **💬 ChatGPT Integration**: Direct integration with OpenAI's GPT models
- **🌐 Web Interface**: Modern web application for easy image upload and result viewing
- **📊 Unified Data Structure**: Consistent JSON format for all analysis results
- **⚡ Incremental Processing**: Smart processing that only analyzes new or changed images
- **📈 Progress Tracking**: Real-time progress bars and status updates
- **🔄 Parallel Processing**: Optional parallel processing for faster batch operations
- **📋 Metadata Extraction**: Comprehensive image metadata and perceptual hashing
- **📊 Results Viewer**: Interactive tool to explore and export analysis results
- **⚙️ Configuration Helper**: Interactive setup wizard for easy configuration
- **🛡️ Error Handling**: Comprehensive error handling with retry mechanisms
- **🏗️ Modern Architecture**: Dependency injection, centralized utilities, and professional code structure

## 🚀 Quick Start

### Option 1: Web Interface (Recommended - Default)

Simply run the application without any arguments to launch the web interface:

```bash
python main.py
```

This will:
- Start the web server automatically
- Open your browser to `http://localhost:5050`
- Allow you to upload images via drag-and-drop
- Start processing with one click
- View results in a beautiful interface
- Download analysis files

### Option 2: Command Line Interface

For command-line usage, use the help menu:

```bash
python main.py --help
```

This will show an interactive menu with all available options.

## 📁 Project Structure

```
CLIP_Analysis/
├── src/                        # Main source code
│   ├── analyzers/              # Analysis modules
│   │   ├── clip_analyzer.py    # CLIP analysis
│   │   ├── llm_analyzer.py     # LLM analysis
│   │   ├── llm_manager.py      # LLM management
│   │   └── metadata_extractor.py # Metadata extraction
│   ├── config/                 # Configuration management
│   │   ├── config_manager.py   # Config utilities
│   │   ├── models.json         # LLM model definitions
│   │   └── prompts.json        # Prompt templates
│   ├── database/               # Database management
│   │   └── db_manager.py       # Database operations
│   ├── processors/             # Batch processing
│   │   └── directory_processor.py # Main processor (with DI)
│   ├── routes/                 # Web routes
│   │   ├── api_routes.py       # API endpoints
│   │   ├── main_routes.py      # Main routes
│   │   └── prompts_routes.py   # Prompt management
│   ├── services/               # Business logic
│   │   ├── analysis_service.py # Analysis orchestration
│   │   ├── clip_service.py     # CLIP API service
│   │   ├── config_service.py   # Configuration service
│   │   └── image_service.py    # Image handling
│   ├── utils/                  # Utility functions
│   │   ├── file_utils.py       # File operations
│   │   ├── progress.py         # Progress tracking
│   │   ├── logger.py           # Logging system
│   │   ├── error_handler.py    # Error handling
│   │   └── wildcard_generator.py # Wildcard generation
│   └── viewers/                # Web interface
│       ├── templates/           # HTML templates
│       └── web_interface.py    # Flask application
├── tests/                      # Test suite
│   ├── run_tests.py           # Unified test runner
│   ├── unit/                   # Unit tests
│   ├── integration/           # Integration tests
│   └── misc/                   # Miscellaneous tests
├── scripts/                    # Utility scripts
│   ├── check_db.py            # Database utilities
│   ├── enable_clip.py         # CLIP setup
│   ├── setup_env.py           # Environment setup
│   └── ...
├── logs/                       # Application logs
├── Images/                     # Input images (not in git)
├── Output/                     # Analysis results (not in git)
├── main.py                     # CLI entry point
├── run_web.py                  # Web interface launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## ⚙️ Configuration

The system uses environment variables for configuration. Copy `secure_env_example.txt` to `.env` and customize:

```bash
# API Configuration
API_BASE_URL=http://localhost:7860
CLIP_MODEL_NAME=ViT-L-14/openai

# Analysis Settings
ENABLE_CLIP_ANALYSIS=True
ENABLE_LLM_ANALYSIS=True
ENABLE_METADATA_EXTRACTION=True
ENABLE_PARALLEL_PROCESSING=False

# Directories
IMAGE_DIRECTORY=Images
OUTPUT_DIRECTORY=Output

# CLIP Modes
CLIP_MODES=best,fast,classic,negative,caption

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Web Interface
WEB_PORT=5050
```

## 🧪 Testing

The project includes a comprehensive test suite with a unified test runner:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suites
python tests/run_tests.py --unit          # Unit tests only
python tests/run_tests.py --integration   # Integration tests
python tests/run_tests.py --web           # Web interface tests
python tests/run_tests.py --fast          # Quick tests only
python tests/run_tests.py --verbose      # Verbose output
python tests/run_tests.py --coverage      # With coverage report
```

## 🏗️ Architecture

### Modern Design Patterns

The codebase uses modern software engineering practices:

- **Dependency Injection**: Core classes accept dependencies for better testability
- **Centralized Utilities**: Common operations in `src/utils/`
- **Service Layer**: Business logic separated from presentation
- **Type Hints**: Comprehensive type annotations throughout
- **Error Handling**: Centralized error handling with context

### Example: Dependency Injection

```python
# Before (tightly coupled)
processor = DirectoryProcessor(config)

# After (dependency injection)
db_manager = DatabaseManager()
llm_manager = LLMManager()
processor = DirectoryProcessor(config, db_manager, llm_manager)

# For testing
mock_db = Mock(spec=DatabaseManager)
mock_llm = Mock(spec=LLMManager)
processor = DirectoryProcessor(config, mock_db, mock_llm)
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jbone3311/CLIP_analysis.git
   cd CLIP_analysis
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp secure_env_example.txt .env
   # Edit .env with your API keys
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

### Development Tools

- **Unified Test Runner**: `python tests/run_tests.py`
- **Code Quality**: Type hints throughout
- **Logging**: Centralized logging system
- **Error Handling**: Comprehensive error context

## 📊 Usage Examples

### Web Interface

1. Start the web server:
   ```bash
   python run_web.py
   ```

2. Open `http://localhost:5050` in your browser

3. Upload images using the drag-and-drop interface

4. Configure analysis settings

5. Start processing

6. View and download results

### Command Line

```bash
# Process images in a directory
python main.py process --input Images --output Output

# View results
python main.py view --input Output

# Configure LLM models
python main.py config llm

# Get help
python main.py --help
```

### Programmatic Usage

```python
from src.processors import DirectoryProcessor
from src.database.db_manager import DatabaseManager
from src.analyzers.llm_manager import LLMManager

# Create dependencies
db_manager = DatabaseManager()
llm_manager = LLMManager()

# Configure
config = {
    'ENABLE_CLIP_ANALYSIS': True,
    'ENABLE_LLM_ANALYSIS': True,
    'IMAGE_DIRECTORY': 'Images',
    'OUTPUT_DIRECTORY': 'Output'
}

# Process images
processor = DirectoryProcessor(config, db_manager, llm_manager)
processor.process_directory()
```

## 🛠️ Advanced Features

### Custom Progress Tracking

```python
from src.utils import ProgressTracker

def my_progress_callback(message):
    print(f"Progress: {message}")

tracker = ProgressTracker(total=100, callback=my_progress_callback)
# Use tracker in your batch operations
```

### File Operations

```python
from src.utils import compute_file_hash, find_image_files

# Compute file hash
md5_hash = compute_file_hash('image.jpg', algorithm='md5')

# Find all images
images = find_image_files('Images/', recursive=True)
```

### Error Handling

```python
from src.utils import handle_errors, ErrorCategory

@handle_errors(ErrorCategory.API, max_retries=3)
def api_call():
    # Your API call here
    pass
```

## 📈 Performance

- **Incremental Processing**: Only processes new/changed images
- **Parallel Processing**: Optional parallel execution
- **Smart Caching**: Avoids redundant API calls
- **Progress Tracking**: Real-time status updates
- **Memory Efficient**: Processes images in batches

## 🔒 Security

- **API Key Management**: Secure environment variable storage
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: No sensitive data in error messages
- **File Security**: Safe file operations with validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python tests/run_tests.py`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CLIP model by OpenAI
- Various LLM providers (OpenAI, Anthropic, Google)
- Flask web framework
- Python community

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `.project-specific/`
- Review the test suite for usage examples

---

**Built with ❤️ using modern Python architecture and best practices.**