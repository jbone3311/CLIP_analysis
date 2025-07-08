# Configuration Guide

## 🔐 Secure Configuration Setup

This project now uses a **secure configuration split** to protect sensitive data:

### 1. **Secure Environment File** (`.env`)
Contains **ONLY** sensitive data like API keys and secrets.

**Setup:**
```bash
# Copy the secure template
cp secure_env_example.txt .env

# Edit .env and add your actual API keys
nano .env
```

**Contains:**
- API keys for all LLM providers
- Database path
- Flask secret key
- API URLs

**⚠️ Security:**
- **NEVER** commit `.env` to version control
- `.env` is already in `.gitignore`
- Keep this file secure and private

### 2. **Public Configuration File** (`config.json`)
Contains all **non-sensitive** configuration that can be safely shared.

**Contains:**
- CLIP configuration
- Analysis features
- Directory paths
- Logging settings
- Web interface settings
- File handling options
- Custom prompts
- Status messages
- Development settings

## 📁 Configuration Files Overview

| File | Purpose | Security | Editable |
|------|---------|----------|----------|
| `.env` | API keys & secrets | 🔒 Private | ✅ Yes |
| `config.json` | Non-sensitive settings | 🌐 Public | ✅ Yes |
| `src/config/models.json` | LLM model definitions | 🌐 Public | ✅ Yes |

## 🔧 How to Configure

### **Adding API Keys:**
1. Copy `secure_env_example.txt` to `.env`
2. Edit `.env` and replace placeholder values:
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   GOOGLE_API_KEY=your-google-key-here
   ```

### **Changing Settings:**
1. Edit `config.json` for most settings
2. Edit `src/config/models.json` for LLM models
3. Restart the application to apply changes

### **Web Interface Configuration:**
1. Start the web interface: `python main.py web`
2. Go to `http://localhost:5051`
3. Use the web interface to modify settings

## 🎛️ Configuration Categories

### **CLIP Analysis:**
```json
{
  "clip_config": {
    "api_base_url": "http://localhost:7860",
    "model_name": "ViT-L-14/openai",
    "clip_modes": ["best", "fast", "classic"],
    "prompt_choices": ["P1", "P2", "P3"]
  }
}
```

### **Analysis Features:**
```json
{
  "analysis_features": {
    "enable_clip_analysis": true,
    "enable_llm_analysis": true,
    "enable_metadata_extraction": true,
    "enable_parallel_processing": false,
    "generate_summaries": true
  }
}
```

### **Web Interface:**
```json
{
  "web_interface": {
    "port": 5051,
    "host": "0.0.0.0",
    "theme": "light",
    "auto_refresh": true
  }
}
```

### **Custom Prompts:**
```json
{
  "custom_prompts": {
    "P1": "Describe this image in detail...",
    "P2": "Analyze the content and mood...",
    "P3": "What objects are depicted..."
  }
}
```

## 🚀 Quick Setup

1. **Copy secure template:**
   ```bash
   cp secure_env_example.txt .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   nano .env
   ```

3. **Customize settings in `config.json`:**
   ```bash
   nano config.json
   ```

4. **Start the application:**
   ```bash
   python main.py web
   ```

## 🔍 Configuration Validation

The application will validate your configuration on startup:

- ✅ Check for required API keys
- ✅ Validate file paths and directories
- ✅ Verify LLM model configurations
- ✅ Test database connectivity

## 🛠️ Troubleshooting

### **Missing API Keys:**
- Ensure `.env` file exists
- Check that API keys are properly formatted
- Verify no extra spaces or quotes

### **Configuration Errors:**
- Check `config.json` syntax (valid JSON)
- Verify file paths exist
- Check log files for detailed errors

### **Web Interface Issues:**
- Check port availability
- Verify firewall settings
- Check `web_interface` settings in `config.json`

## 📝 Environment Variables Reference

### **Required (in .env):**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `FLASK_SECRET_KEY` - Flask session secret

### **Optional (in .env):**
- `GROK_API_KEY` - Grok API key
- `COHERE_API_KEY` - Cohere API key
- `MISTRAL_API_KEY` - Mistral API key
- `PERPLEXITY_API_KEY` - Perplexity API key
- `DATABASE_PATH` - Database file path

### **API URLs (usually don't change):**
- `OPENAI_URL` - OpenAI API endpoint
- `ANTHROPIC_URL` - Anthropic API endpoint
- `GOOGLE_URL` - Google API endpoint
- `OLLAMA_URL` - Ollama server URL

## 🔄 Migration from Old Configuration

If you have an old `.env` file with all settings:

1. **Extract API keys** to new `.env`
2. **Move other settings** to `config.json`
3. **Delete old `.env`** file
4. **Test configuration** with `python main.py web`

## 📚 Advanced Configuration

### **Custom LLM Models:**
Edit `src/config/models.json` to add custom models or modify existing ones.

### **Database Configuration:**
Change `DATABASE_PATH` in `.env` to use a different database file.

### **Logging Configuration:**
Modify the `logging` section in `config.json` to adjust log levels and file settings.

### **File Processing:**
Adjust `file_handling` settings in `config.json` for different file types and sizes. 