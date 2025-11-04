# Complete Configuration Guide

## 📍 **Single Source of Truth**

**Configuration is managed in TWO files:**

1. **`.env` file** - Private/sensitive data (API keys, passwords, secrets)
   - Location: Root directory (`.env`)
   - Template: `secure_env_example.txt`
   - **Never commit to git!**

2. **`config.json` file** - Public settings (features, UI preferences)
   - Location: Root directory (`config.json`)
   - Can be safely committed to git

---

## 🔧 **How Configuration Works**

### **Option 1: Direct Environment Variables (Current)**
Most code uses `os.getenv()` directly:
```python
api_url = os.getenv('CLIP_API_URL', 'http://localhost:7860')
password = os.getenv('CLIP_API_PASSWORD')
```

### **Option 2: Config Manager (Recommended for new code)**
Use the centralized config manager:
```python
from src.config.config_manager import get_combined_config

config = get_combined_config()
clip_url = config['private']['clip_api_url']
password = config['private']['clip_api_password']
```

---

## 📋 **All Configuration Variables**

### **CLIP API Configuration**
```bash
CLIP_API_URL=http://localhost:7860              # Base URL for CLIP API
CLIP_API_PASSWORD=your_password                  # Password for authenticated APIs
CLIP_MODEL_NAME=ViT-L-14/openai                  # CLIP model to use
CLIP_MODES=best,fast,classic,negative,caption    # Analysis modes
CLIP_API_TIMEOUT=300                              # Request timeout in seconds
```

### **LLM API Keys**
```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
GROK_API_KEY=your_key
COHERE_API_KEY=your_key
MISTRAL_API_KEY=your_key
PERPLEXITY_API_KEY=your_key
```

### **LLM API URLs**
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

### **Database Configuration**
```bash
DATABASE_PATH=image_analysis.db
DATABASE_URL=sqlite:///image_analysis.db
```

### **Web Server Configuration**
```bash
WEB_PORT=5050
SECRET_KEY=your_secret_key_here
FLASK_SECRET_KEY=your-secret-key-here
```

### **Analysis Settings** (in `config.json`)
```json
{
  "clip_config": {
    "api_base_url": "http://localhost:7860",
    "model_name": "ViT-L-14/openai",
    "enable_clip_analysis": true,
    "clip_modes": ["best", "fast", "classic"],
    "prompt_choices": ["P1", "P2", "P3"]
  },
  "analysis_features": {
    "enable_llm_analysis": true,
    "enable_metadata_extraction": true,
    "enable_parallel_processing": false,
    "generate_summaries": true
  }
}
```

---

## 🎯 **Quick Setup**

1. **Copy the example file:**
   ```bash
   cp secure_env_example.txt .env
   ```

2. **Edit `.env` with your actual values:**
   ```bash
   nano .env  # or use your favorite editor
   ```

3. **Create `config.json` (optional, defaults are used if missing):**
   ```bash
   python -m src.config.config_manager
   ```

4. **Verify configuration:**
   ```python
   from src.config.config_manager import validate_config
   issues = validate_config()
   print(issues)
   ```

---

## ⚠️ **Important Notes**

1. **Variable Name Consistency:**
   - Old code may use `API_BASE_URL` (deprecated)
   - New code should use `CLIP_API_URL`
   - Both are supported, but `CLIP_API_URL` is preferred

2. **Configuration Priority:**
   - Environment variables (`.env`) take precedence
   - `config.json` provides defaults
   - Command-line arguments override both

3. **Security:**
   - Never commit `.env` to git
   - Always use `secure_env_example.txt` as template
   - Keep API keys and passwords secret

---

## 🔄 **Migration Path**

To consolidate all configuration through `config_manager.py`:

1. Update all modules to use `get_combined_config()` instead of direct `os.getenv()`
2. Update `config_manager.py` to include all variables
3. Ensure `secure_env_example.txt` matches what `config_manager` expects

**Current Status:** Mixed - some code uses direct `os.getenv()`, some uses `config_manager`

---

## 📚 **Related Files**

- `src/config/config_manager.py` - Main configuration manager
- `src/services/config_service.py` - Service wrapper for config manager
- `secure_env_example.txt` - Template for `.env` file
- `config.json` - Public configuration (auto-generated if missing)

---

**Last Updated:** 2025-01-XX

