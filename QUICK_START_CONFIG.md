# Quick Start Configuration Guide 🚀

**Everything is up to date and clean!** ✅

---

## 📋 **Project Status**

✅ **Code Quality:** No linter errors  
✅ **Configuration:** Centralized and typed  
✅ **Packaging:** Modern `pyproject.toml`  
✅ **Pre-commit:** Hooks configured  
✅ **Documentation:** Complete  

---

## ⚙️ **Quick Configuration (3 Steps)**

### **Step 1: Copy the Example File**

```bash
cp secure_env_example.txt .env
```

### **Step 2: Edit `.env` File**

Open `.env` in your editor and add your API keys:

```bash
# Required: CLIP API Configuration
CLIP_API_URL=https://your-clip-api-url.com

# Optional: CLIP API Password (only if your API requires authentication)
# Leave empty if not needed
CLIP_API_PASSWORD=your_password_here

# These are already set with defaults, but you can customize:
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,classic,negative,caption
CLIP_API_TIMEOUT=300

# Optional: LLM API Keys (only if you want LLM analysis)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
# ... etc
```

**Minimum required:**
- `CLIP_API_URL` - Your CLIP API endpoint
- `CLIP_API_PASSWORD` - If your API requires authentication

**Everything else is optional!**

### **Step 3: Verify Configuration**

```bash
python -m src.config.config_manager
```

This will:
- ✅ Create `.env` if missing
- ✅ Create `config.json` if missing
- ✅ Validate your configuration
- ✅ Show any issues

---

## 🎯 **For Developers (Optional Setup)**

### **1. Install Pre-commit Hooks**

```bash
pip install pre-commit
pre-commit install
```

This automatically checks code quality on every commit.

### **2. Use Typed Configuration (Optional)**

```python
from src.config import load_typed_config

config = load_typed_config()
api_url = config.clip.api_url  # Type-safe!
password = config.clip.api_password
```

---

## 📝 **Configuration Files**

### **`.env` File** (Private - Never Commit!)
Contains:
- API keys and passwords
- Sensitive configuration
- Database paths
- Web server settings

### **`config.json` File** (Public - Can Commit)
Contains:
- Feature flags (CLIP analysis on/off, etc.)
- UI preferences
- Analysis settings

**Auto-created if missing!**

---

## 🔍 **What Each Variable Does**

### **CLIP API (Required)**
```bash
CLIP_API_URL=http://localhost:7860              # Your CLIP API endpoint
CLIP_API_PASSWORD=password                      # Password for authenticated APIs
CLIP_MODEL_NAME=ViT-L-14/openai                # CLIP model to use
CLIP_MODES=best,fast,classic,negative,caption   # Analysis modes
CLIP_API_TIMEOUT=300                            # Request timeout (seconds)
```

### **LLM APIs (Optional)**
```bash
OPENAI_API_KEY=your_key                         # OpenAI API key
ANTHROPIC_API_KEY=your_key                     # Anthropic API key
# ... etc (only needed if using LLM analysis)
```

### **Web Server (Optional)**
```bash
WEB_PORT=5050                                   # Web interface port
FLASK_SECRET_KEY=your-secret-key                # Flask secret (change in production!)
```

### **Database (Optional)**
```bash
DATABASE_PATH=image_analysis.db                  # SQLite database path
```

---

## 🚀 **Quick Test**

After configuration, test it:

```bash
# Test CLIP analyzer
python -m src.analyzers.clip_analyzer Images/test.jpg --validate

# Run web interface
python main.py web

# Or use the CLI
python main.py process --input Images --output Output
```

---

## ✅ **Configuration Checklist**

- [ ] Copied `secure_env_example.txt` to `.env`
- [ ] Added `CLIP_API_URL` to `.env`
- [ ] Added `CLIP_API_PASSWORD` (if needed)
- [ ] Added LLM API keys (if using LLM analysis)
- [ ] Ran `python -m src.config.config_manager` to verify
- [ ] Tested with a sample image

---

## 🆘 **Troubleshooting**

### **"Module not found" errors**
```bash
pip install -r requirements.txt
```

### **"Configuration not found"**
```bash
python -m src.config.config_manager
```

### **"API authentication failed"**
- Check `CLIP_API_URL` is correct
- Check `CLIP_API_PASSWORD` is set (if required)
- Verify your API is accessible

### **Need help?**
- Check `CONFIGURATION_GUIDE_COMPLETE.md` for detailed docs
- Check `AUTHENTICATED_CLIP_USAGE.md` for CLIP API setup
- Check `CLIP_API_GUIDE.md` for API reference

---

## 📚 **Advanced Configuration**

### **Using Typed Config (Recommended for New Code)**

```python
from src.config import load_typed_config, AppConfig

# Load typed configuration
config: AppConfig = load_typed_config()

# Access with type safety
api_url = config.clip.api_url
password = config.clip.api_password
port = config.web.port
enable_clip = config.analysis.enable_clip_analysis
```

### **Using Legacy Config (Backward Compatible)**

```python
from src.config import get_all_config

# Get all config as dictionary
config = get_all_config()

# Access like before
api_url = config['CLIP_API_URL']
password = config['CLIP_API_PASSWORD']
```

---

**That's it! You're ready to go!** 🎉

