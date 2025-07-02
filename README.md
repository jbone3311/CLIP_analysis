# Dual-Mode Image Analysis Tool

A comprehensive Python-based image analysis solution that combines the power of Large Language Models (LLMs) and CLIP Interrogator technology to provide detailed image analysis, descriptions, and prompt generation.

## 🚀 Features

### Dual Analysis Modes
- **LLM Analysis**: Uses various LLM APIs (GPT-4, Claude, etc.) for detailed image descriptions and creative interpretations
- **CLIP Interrogator Analysis**: Leverages CLIP models for caption generation and prompt creation in multiple modes

### Key Capabilities
- **Batch Processing**: Process entire directories of images recursively
- **Multiple LLM Support**: Configure up to 5 different LLM providers/models
- **CLIP Modes**: Support for `best`, `fast`, `classic`, `negative`, and `caption` analysis modes
- **Flexible Storage**: JSON file output with optional database storage
- **Smart Duplicate Detection**: Avoid reprocessing with file hash comparison
- **Configurable Prompts**: Customizable analysis prompts via JSON configuration
- **Retry Mechanisms**: Built-in retry logic with exponential backoff
- **Comprehensive Logging**: Detailed logging with configurable emoji status indicators

## 📁 Project Structure

```
├── analysis_LLM.py          # LLM-based image analysis engine
├── analysis_interrogate.py  # CLIP Interrogator analysis engine
├── directory_processor.py   # Batch processing for image directories
├── config.py               # Configuration management
├── db_utils.py            # Database utilities for tracking processed images
├── utils.py               # Helper functions and utilities
├── LLM_Prompts.json       # Configurable LLM analysis prompts
├── .env                   # Environment configuration (create from .env copy)
└── README.md             # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**
   ```bash
   pip install requests python-dotenv argparse
   ```

3. **Configure environment**
   ```bash
   cp ".env copy" .env
   # Edit .env with your API keys and settings
   ```

## ⚙️ Configuration

### Environment Variables

Configure the tool via the `.env` file:

#### LLM Configuration (up to 5 models)
```env
LLM_1_TITLE=GPT-4 Vision
LLM_1_API_URL=https://api.openai.com/v1/chat/completions
LLM_1_API_KEY=your_openai_api_key
LLM_1_MODEL=gpt-4-vision-preview

LLM_2_TITLE=Claude 3 Vision
LLM_2_API_URL=https://api.anthropic.com/v1/messages
LLM_2_API_KEY=your_anthropic_api_key
LLM_2_MODEL=claude-3-opus-20240229
```

#### CLIP Interrogator Configuration
```env
API_BASE_URL=http://localhost:7860
CLIP_MODEL_NAME=ViT-L-14/openai
```

#### Processing Settings
```env
IMAGE_DIRECTORY=Images
OUTPUT_DIRECTORY=Output
ENABLE_LLM_ANALYSIS=true
ENABLE_CLIP_ANALYSIS=true
ENABLE_CAPTION=true
ENABLE_BEST=true
ENABLE_FAST=true
ENABLE_CLASSIC=true
ENABLE_NEGATIVE=true
```

#### Storage Options
```env
USE_JSON=true
USE_DATABASE=false
DATABASE_PATH=image_analysis.db
```

## 🚀 Usage

### Single Image Analysis

#### LLM Analysis
```bash
python analysis_LLM.py image.jpg --prompt "PROMPT1,PROMPT2" --model 1 --output results.json
```

#### CLIP Interrogator Analysis
```bash
python analysis_interrogate.py image.jpg --modes best fast classic --output output.json
```

### Batch Directory Processing
```bash
python directory_processor.py
```

### Available Commands

#### List Available Models
```bash
python analysis_LLM.py --model list
```

#### List Available Prompts
```bash
python analysis_LLM.py --prompt list
```

## 📊 Output Format

### JSON Structure
Each processed image generates a JSON file with the following structure:

```json
{
    "image": "/absolute/path/to/image.jpg",
    "model": "gpt-4-vision-preview",
    "prompts": {
        "results": [
            {
                "prompt": "PROMPT1",
                "result": {
                    "choices": [...],
                    "usage": {...}
                }
            }
        ]
    },
    "analysis": {
        "best": "Generated prompt...",
        "fast": "Quick description...",
        "classic": "Classic style prompt...",
        "negative": "Negative prompt...",
        "caption": "Image caption..."
    }
}
```

## 🎯 Analysis Modes

### LLM Prompts (Configurable via LLM_Prompts.json)

1. **PROMPT1**: Detailed Image Description
   - Comprehensive visual analysis
   - Objective descriptions for accessibility
   - Temperature: 0.7, Max Tokens: 1000

2. **PROMPT2**: Art Critique from Multiple Perspectives
   - Analysis from 6 different viewpoints (Artist, Gallery Owner, Curator, 12-year-old, 19-year-old, 50-year-old)
   - Creative interpretations and emotional responses
   - Temperature: 0.8, Max Tokens: 1500

### CLIP Interrogator Modes

- **best**: Highest quality prompt generation
- **fast**: Quick prompt generation
- **classic**: Traditional style prompts
- **negative**: Negative prompts for AI art generation
- **caption**: Simple image captions

## 🔧 Advanced Features

### Smart Processing
- **File Hash Comparison**: Automatically detects if images have been modified
- **Incremental Processing**: Only runs missing analysis modes
- **Error Handling**: Graceful error recovery with detailed logging

### Database Support
- Optional SQLite database for tracking processed images
- Status tracking (processing, completed, failed)
- Prevents duplicate processing across sessions

### Logging and Monitoring
- Configurable emoji status indicators
- Detailed error reporting
- API conversation logging (optional)

## 🛡️ Error Handling

The tool includes comprehensive error handling:
- Automatic retry with exponential backoff
- Graceful API failure recovery
- Detailed error logging
- Processing status tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify your API keys and endpoints
3. Ensure required dependencies are installed
4. Create an issue in the repository

## 🔮 Future Enhancements

- Web-based user interface
- Additional LLM provider support
- Batch prompt customization
- Result aggregation and comparison tools
- Export formats (CSV, XML, etc.)