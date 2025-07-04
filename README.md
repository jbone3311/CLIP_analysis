# Image Analysis with CLIP and LLM

A comprehensive image analysis system that combines CLIP (Contrastive Language-Image Pre-training) and LLM (Large Language Model) technologies to provide detailed analysis of images. This system processes images in batches, generates descriptive captions, and creates prompt lists for various AI applications.

## ✨ Key Features

- **🔍 CLIP Analysis**: Multi-mode image analysis using CLIP interrogator
- **🤖 LLM Analysis**: Advanced text generation using multiple LLM models
- **🌐 Web Interface**: Modern web application for easy image upload and result viewing
- **📊 Unified Data Structure**: Consistent JSON format for all analysis results
- **⚡ Incremental Processing**: Smart processing that only analyzes new or changed images
- **📈 Progress Tracking**: Real-time progress bars and status updates
- **🔄 Parallel Processing**: Optional parallel processing for faster batch operations
- **📋 Metadata Extraction**: Comprehensive image metadata and perceptual hashing
- **📊 Results Viewer**: Interactive tool to explore and export analysis results
- **⚙️ Configuration Helper**: Interactive setup wizard for easy configuration
- **🛡️ Error Handling**: Comprehensive error handling with retry mechanisms

## 🚀 Quick Start

### Option 1: Web Interface (Recommended - Default)

Simply run the application without any arguments to launch the web interface:

```bash
python main.py
```

This will:
- Start the web server automatically
- Open your browser to `http://localhost:5000`
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

### 1. Setup Configuration

Run the interactive configuration helper:

```bash
python main.py config
```

Or use the legacy command:

```bash
python src/config/config_manager.py
```

This will guide you through setting up:
- API endpoints and keys
- CLIP and LLM model configurations
- Directory paths
- Processing options

### 2. Add Images

Place your images in the `Images` directory (or your configured image directory).

### 3. Run Analysis

#### Option A: Web Interface (Recommended)
Start the web interface for an easy-to-use graphical interface:

```bash
python main.py web
```

Then open your browser to `http://localhost:5000` and:
- Upload images via drag-and-drop
- Start processing with one click
- View results in a beautiful interface
- Download analysis files

#### Option B: Command Line
```bash
python main.py process
```

Or use the legacy command:

```bash
python directory_processor.py
```

### 4. View Results

#### Option A: Web Interface
Navigate to the Results page in the web interface for:
- Interactive filtering and search
- Quick preview of analysis results
- Download individual or bulk results
- Visual status indicators

#### Option B: Command Line
```bash
# List all analysis files
python main.py view --list

# View a specific file
python main.py view --file Output/image_analysis.json

# Generate summary report
python main.py view --summary

# Export results to CSV
python main.py view --export csv --output results.csv
```

Or use the legacy commands:

```bash
# List all analysis files
python src/viewers/results_viewer.py --list

# View a specific file
python src/viewers/results_viewer.py --file Output/image_analysis.json
```

## 🌐 Web Interface

The web interface provides a modern, user-friendly way to interact with the image analysis system:

### Features
- **📤 Drag & Drop Upload**: Easy image upload with support for multiple files
- **📊 Real-time Dashboard**: Monitor system status and recent activity
- **🔍 Interactive Results**: Search, filter, and explore analysis results
- **⚙️ Configuration Management**: Web-based settings configuration
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🔄 Background Processing**: Start processing and continue browsing
- **🌐 Auto Browser Opening**: Browser opens automatically when you start the web interface

### Getting Started
1. Start the web interface: `python main.py` (default) or `python main.py web`
2. Your browser will open automatically to `http://localhost:5000`
3. Upload images using the Upload page
4. Start processing from the Process page
5. View results in the Results page
6. Configure settings in the Config page

### Web Interface Pages
- **Dashboard**: Overview of system status and recent activity
- **Upload**: Drag-and-drop image upload with folder organization
- **Images**: Browse and manage uploaded images
- **Process**: Start and monitor image processing
- **Results**: View, search, and download analysis results
- **Config**: Manage system configuration settings

## 📁 Project Structure

```
GIT_CLIP_Analysis/
├── src/                     # Source code package
│   ├── __init__.py
│   ├── analyzers/           # Analysis modules
│   │   ├── __init__.py
│   │   ├── clip_analyzer.py     # CLIP analysis
│   │   ├── llm_analyzer.py      # LLM analysis
│   │   └── metadata_extractor.py # Metadata extraction
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── viewers/             # Results viewing tools
│   │   ├── __init__.py
│   │   ├── results_viewer.py    # Command-line viewer
│   │   ├── web_interface.py     # Flask web application
│   │   └── templates/           # HTML templates
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── upload.html
│   │       ├── results.html
│   │       ├── process.html
│   │       ├── config.html
│   │       ├── images.html
│   │       └── result_detail.html
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── installer.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── unit/                # Unit tests
│   │   ├── __init__.py
│   │   ├── test_clip_analyzer.py
│   │   ├── test_llm_analyzer.py
│   │   └── test_metadata_extractor.py
│   ├── integration/         # Integration tests
│   │   ├── __init__.py
│   │   └── test_system.py
│   ├── fixtures/            # Test data
│   └── run_tests.py         # Test runner
├── config/                  # Configuration files
│   └── prompts.json         # LLM prompt definitions
├── examples/                # Example scripts
│   └── basic_usage.py
├── docs/                    # Documentation
├── Images/                  # Input image directory
├── Output/                  # Analysis results directory
├── main.py                  # Main entry point
├── directory_processor.py   # Legacy main processor
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── pytest.ini              # Test configuration
├── Makefile                 # Development tasks
├── .env                     # Configuration file (generated)
└── README.md               # This file
```

## 🔧 Configuration

The system uses a `.env` file for configuration. Key settings include:

### Processing Settings
- `ENABLE_PARALLEL_PROCESSING`: Enable parallel processing (default: False)
- `ENABLE_METADATA_EXTRACTION`: Extract image metadata (default: True)
- `FORCE_REPROCESS`: Force reprocessing of existing files (default: False)
- `GENERATE_SUMMARIES`: Generate summary files (default: True)

### CLIP Settings
- `API_BASE_URL`: CLIP API endpoint (default: http://localhost:7860)
- `CLIP_MODEL_NAME`: CLIP model to use (default: ViT-L-14/openai)
- `ENABLE_CLIP_ANALYSIS`: Enable CLIP analysis (default: True)
- `CLIP_MODES`: Analysis modes (default: best,fast)

### LLM Settings
- `ENABLE_LLM_ANALYSIS`: Enable LLM analysis (default: True)
- `PROMPT_CHOICES`: Prompts to use (default: P1,P2)
- `LLM_1_TITLE`, `LLM_1_API_URL`, `LLM_1_API_KEY`, `LLM_1_MODEL`: Model 1 configuration
- (Repeat for additional models)

### Directory Settings
- `IMAGE_DIRECTORY`: Input image directory (default: Images)
- `OUTPUT_DIRECTORY`: Output results directory (default: Output)

## 📊 Data Structure

Each image generates a unified JSON file with the following structure:

```json
{
  "file_info": {
    "filename": "image.jpg",
    "directory": "Images",
    "date_added": "2024-01-01T12:00:00",
    "date_processed": "2024-01-01T12:01:30",
    "md5": "abc123...",
    "file_size": 1024000
  },
  "analysis": {
    "clip": {
      "best": {"prompt": "..."},
      "fast": {"prompt": "..."}
    },
    "llm": [
      {
        "prompt": "P1",
        "result": {...},
        "status": "success"
      }
    ],
    "metadata": {
      "width": 1920,
      "height": 1080,
      "format": "JPEG",
      "color_mode": "RGB"
    }
  },
  "processing_info": {
    "config_used": {...},
    "processing_time": 45.2,
    "status": "complete",
    "errors": []
  }
}
```

## 🛠️ Usage Examples

### Basic Processing

```bash
# Process all images in the Images directory
python directory_processor.py
```

### Standalone CLIP Analysis

```bash
# Analyze a single image with CLIP
python src/analyzers/clip_analyzer.py image.jpg --modes best fast --output result.json

# Validate CLIP configuration
python src/analyzers/clip_analyzer.py --validate
```

### Standalone LLM Analysis

```bash
# Analyze a single image with LLM
python src/analyzers/llm_analyzer.py image.jpg --model 1 --prompt P1,P2 --output result.json

# List available models
python src/analyzers/llm_analyzer.py --list-models

# List available prompts
python src/analyzers/llm_analyzer.py --list-prompts
```

### Results Exploration

```bash
# List all analysis files
python main.py view --list

# View detailed results for a specific file
python main.py view --file Output/image_analysis.json

# Generate summary report
python main.py view --summary --output summary.json

# Export to CSV
python main.py view --export csv --output results.csv
```

## 🔍 Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF
- WebP

## 🤖 Supported LLM Models

The system supports multiple LLM models simultaneously:

1. **OpenAI GPT Models** (GPT-4, GPT-4o, etc.)
2. **Anthropic Claude** (Claude-3, etc.)
3. **Local Models** (Ollama, etc.)
4. **Custom API Endpoints**

## 📝 Available Prompts

### P1: Detailed Image Description
Comprehensive description following a structured approach covering main subject, setting, details, colors, composition, and more.

### P2: Art Critique from Multiple Perspectives
Analysis from different viewpoints: artist, gallery owner, curator, and various age groups.

## ⚡ Performance Features

- **Incremental Processing**: Only processes new or changed images
- **Parallel Processing**: Optional multi-threaded processing
- **Progress Tracking**: Real-time progress bars and ETA
- **Error Recovery**: Automatic retry with exponential backoff
- **Memory Efficient**: Processes images in chunks

## 🔧 Advanced Configuration

### Custom Prompts

Edit `LLM_Prompts.json` to add custom prompts:

```json
{
  "CUSTOM_PROMPT": {
    "TITLE": "Custom Analysis",
    "PROMPT_TEXT": "Your custom prompt here...",
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 1500
  }
}
```

### Environment Variables

Set additional environment variables for fine-tuning:

```bash
LOGGING_LEVEL=DEBUG
RETRY_LIMIT=10
TIMEOUT=120
```

## 🐛 Troubleshooting

### Common Issues

1. **CLIP API Connection Failed**
   - Check if CLIP API is running at the configured URL
   - Verify network connectivity
   - Check API endpoint configuration

2. **LLM API Authentication Failed**
   - Verify API keys are correct
   - Check API endpoint URLs
   - Ensure sufficient API credits

3. **No Images Found**
   - Verify image directory path
   - Check file permissions
   - Ensure images are in supported formats

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
LOGGING_LEVEL=DEBUG python directory_processor.py
```

## 📈 Monitoring and Logs

- **Console Output**: Real-time progress and status
- **Log File**: Detailed logs saved to `processing.log`
- **Results Viewer**: Interactive exploration of results
- **Summary Reports**: Automated summary generation

## 🧪 Testing and Development

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run unit tests only
python tests/run_tests.py unit

# Run integration tests only
python tests/run_tests.py integration

# Run specific test
python tests/run_tests.py specific clip_analyzer
```

### Using Makefile (Development)

```bash
# Show all available commands
make help

# Setup development environment
make dev-setup

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Quick development cycle
make quick-test
```

### Using pytest

```bash
# Run all tests with pytest
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_clip_analyzer.py

# Run tests with markers
pytest -m unit
pytest -m integration
```

## 🔄 Incremental Processing

The system automatically detects:
- New images that haven't been processed
- Modified images (using MD5 hash comparison)
- Images with missing analysis types

Use `FORCE_REPROCESS=true` to reprocess all images.

## 📊 Output Organization

Results are organized in the output directory:
- `{filename}_analysis.json`: Complete analysis for each image
- `clip_analysis_summary.json`: Summary of all CLIP results
- `llm_analysis_summary.json`: Summary of all LLM results
- `metadata_summary.json`: Summary of all metadata

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for CLIP and GPT models
- Anthropic for Claude models
- The open-source community for various dependencies

---

**Happy Image Analyzing! 🖼️✨**