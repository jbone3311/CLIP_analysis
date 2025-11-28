# Configuration Guide

This guide explains how to configure the CLIP Analysis system. Configuration is managed through two files: `.env` (private/sensitive data) and `config.json` (public settings).

## Quick Start

1. **Copy the example file:**
   ```bash
   cp secure_env_example.txt .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   # Required: CLIP API Configuration
   CLIP_API_URL=http://localhost:7860
   
   # Optional: CLIP API Password (only if your API requires authentication)
   CLIP_API_PASSWORD=
   
   # Optional: LLM API Keys (only if using LLM analysis)
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Verify configuration:**
   ```bash
   python -m src.config.config_manager
   ```

## Configuration Files

### `.env` File (Private - Never Commit!)

Contains sensitive data:
- API keys and passwords
- Database paths
- Secret keys
- Server settings

**Template:** `secure_env_example.txt`  
**Location:** Root directory  
**Security:** Never commit to git!

### `config.json` File (Public - Can Commit)

Contains public settings:
- Feature flags (CLIP analysis on/off, etc.)
- UI preferences
- Analysis settings

**Location:** Root directory  
**Auto-created:** If missing, defaults are used

## Configuration Variables

### CLIP API Configuration (Required)

```bash
CLIP_API_URL=http://localhost:7860              # Base URL for CLIP API
CLIP_API_PASSWORD=                              # Password for authenticated APIs (optional)
CLIP_MODEL_NAME=ViT-L-14/openai                # CLIP model to use
CLIP_MODES=best,fast,classic,negative,caption  # Analysis modes (comma-separated)
CLIP_API_TIMEOUT=300                            # Request timeout in seconds
```

### LLM API Keys (Optional)

Only needed if using LLM analysis:

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
GROK_API_KEY=your_key
COHERE_API_KEY=your_key
MISTRAL_API_KEY=your_key
PERPLEXITY_API_KEY=your_key
```

### LLM API URLs (Optional)

Usually don't need to change:

```bash
OPENAI_URL=https://api.openai.com/v1
ANTHROPIC_URL=https://api.anthropic.com/v1
GOOGLE_URL=https://generativelanguage.googleapis.com/v1
GROK_URL=https://api.x.ai/v1
COHERE_URL=https://api.cohere.ai/v1
MISTRAL_URL=https://api.mistral.ai/v1
PERPLEXITY_URL=https://api.perplexity.ai
OLLAMA_URL=http://localhost:11434
```

### Database Configuration

```bash
DATABASE_PATH=image_analysis.db
DATABASE_URL=sqlite:///image_analysis.db
```

### Web Server Configuration

```bash
WEB_PORT=5050
FLASK_SECRET_KEY=your-secret-key-here          # Change in production!
SECRET_KEY=your_secret_key_here                # Change in production!
```

### Analysis Settings (Optional)

```bash
ENABLE_CLIP_ANALYSIS=True
ENABLE_LLM_ANALYSIS=True
ENABLE_METADATA_EXTRACTION=True
ENABLE_PARALLEL_PROCESSING=False
GENERATE_SUMMARIES=True
FORCE_REPROCESS=False
DEBUG=False
```

### Directory Configuration (Optional)

```bash
IMAGE_DIRECTORY=Images                          # Default: Images
OUTPUT_DIRECTORY=Output                         # Default: Output
```

### Logging Configuration (Optional)

```bash
LOG_LEVEL=INFO                                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=app.log
ERROR_LOG_FILE=errors.log
LOG_MAX_SIZE=10485760                           # 10MB
LOG_BACKUP_COUNT=5
```

## Configuration Priority

1. **Environment variables** (`.env`) - Highest priority
2. **config.json** - Default values
3. **Function defaults** - Fallback values

## Using Configuration in Code

### Option 1: Direct Environment Variables

```python
import os

api_url = os.getenv('CLIP_API_URL', 'http://localhost:7860')
password = os.getenv('CLIP_API_PASSWORD')
```

### Option 2: Config Manager (Recommended)

```python
from src.config.config_manager import get_config_value

api_url = get_config_value('CLIP_API_URL', 'http://localhost:7860')
password = get_config_value('CLIP_API_PASSWORD')
port = get_config_value('WEB_PORT', 5050)  # Auto-converts to int!
```

### Option 3: Typed Configuration (Advanced)

```python
from src.config import load_typed_config, AppConfig

config: AppConfig = load_typed_config()
api_url = config.clip.api_url
password = config.clip.api_password
port = config.web.port
```

## Important Notes

1. **Variable Names:**
   - Use `CLIP_API_URL` (not deprecated `API_BASE_URL`)
   - All variable names are case-sensitive

2. **Security:**
   - Never commit `.env` to git
   - Always use `secure_env_example.txt` as template
   - Keep API keys and passwords secret
   - Change secret keys in production

3. **Validation:**
   - Run `python -m src.config.config_manager` to validate
   - Check logs for configuration errors

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Configuration not found"
```bash
python -m src.config.config_manager
```

### "API authentication failed"
- Check `CLIP_API_URL` is correct
- Check `CLIP_API_PASSWORD` is set (if required)
- Verify your API is accessible

### Need more help?
- See `CLIP_API.md` for CLIP API setup
- See `README.md` for general usage
- Check `.project-specific/docs/` for detailed documentation

## Related Files

- `secure_env_example.txt` - Template for `.env` file
- `src/config/config_manager.py` - Main configuration manager
- `src/services/config_service.py` - Service wrapper for config manager
- `config.json` - Public configuration (auto-generated if missing)

