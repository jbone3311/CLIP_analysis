# Using CLIP Analysis with Authenticated APIs

## 🎉 Your Setup is Complete!

Your CLIP analyzer now fully supports **Stable Diffusion Forge** with Pinokio authentication!

---

## ⚙️ Configuration

### 1. Update Your `.env` File

```bash
# Copy the example if you haven't already
cp secure_env_example.txt .env

# Edit .env and add these lines:
```

```bash
# CLIP API Configuration (Stable Diffusion Forge)
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_API_PASSWORD=jbone3311
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,negative
CLIP_API_TIMEOUT=300
```

---

## 🚀 Usage

### Option 1: Using Environment Variables (Recommended)

Once your `.env` is configured, simply run:

```bash
# Analyze a single image
python -m src.analyzers.clip_analyzer Images/test.jpg

# Analyze with custom output
python -m src.analyzers.clip_analyzer Images/test.jpg --output my_results.json

# Force reprocessing (skip cache)
python -m src.analyzers.clip_analyzer Images/test.jpg --force

# Validate configuration first
python -m src.analyzers.clip_analyzer Images/test.jpg --validate
```

The analyzer will automatically:
- ✅ Read your API URL from `.env`
- ✅ Use your password from `.env`
- ✅ Authenticate with the API
- ✅ Cache the session for subsequent requests

---

### Option 2: Command Line Arguments

You can override environment variables with command line arguments:

```bash
python -m src.analyzers.clip_analyzer Images/test.jpg \
  --api_base_url https://briefly-charleston-verified-individuals.trycloudflare.com \
  --password jbone3311 \
  --model ViT-L-14/openai \
  --modes best fast negative \
  --output results.json
```

---

### Option 3: Programmatic Usage

```python
from src.analyzers.clip_analyzer import process_image_with_clip
import os

# Configuration
api_url = os.getenv("CLIP_API_URL")
password = os.getenv("CLIP_API_PASSWORD")  
model = "ViT-L-14/openai"
modes = ["best", "fast", "negative"]

# Process image with authentication
result = process_image_with_clip(
    image_path="Images/test.jpg",
    api_base_url=api_url,
    model=model,
    modes=modes,
    password=password  # <-- Authentication happens automatically
)

if result["status"] == "success":
    print(f"✅ Analysis complete!")
    print(f"Prompts: {result['prompt']}")
else:
    print(f"❌ Error: {result['message']}")
```

---

## 🔑 How Authentication Works

### Session Management

The analyzer automatically handles authentication:

1. **First Request:**
   - Logs in to your API with password
   - Gets session cookie
   - Caches session for reuse

2. **Subsequent Requests:**
   - Reuses cached session (no login needed)
   - Validates session is still active
   - Re-authenticates if session expired

3. **Multiple Images:**
   - Only authenticates once
   - All images use same session
   - Fast and efficient!

### Authentication Flow

```
Your Code → get_authenticated_session()
                    ↓
         Session Cached? → Yes → Use Cached Session
                    ↓ No
         POST /pinokio/login
                    ↓
         Get Session Cookie
                    ↓
         Cache for Reuse
                    ↓
         Return Authenticated Session
```

---

## 🧪 Testing Your Setup

### Quick Test

```bash
# Test authentication and API access
python scripts/test_clip_api_auth.py
```

**Expected Output:**
```
🔐 Step 1: Authenticating...
✅ Successfully authenticated!

🧪 Step 2: Testing CLIP Interrogator API
✅ List CLIP Models: Found 87 items
✅ API Info: Working
✅ API Config: Working
```

### Test with Real Image

```bash
# Analyze the test image
python -m src.analyzers.clip_analyzer Images/test.jpg

# Expected output:
# Authenticating with CLIP API...
# ✅ Successfully authenticated with CLIP API
# Starting CLIP analysis for Images/test.jpg
# ✅ CLIP analysis completed successfully
```

---

## 📊 Available CLIP Models

Your API has **87 CLIP models** available! Some popular ones:

### Best Quality:
- `ViT-L-14/openai` ⭐ (Recommended)
- `ViT-L-14/laion2b_s32b_b82k`
- `ViT-B-16/openai`

### Fast:
- `ViT-B-32/openai`
- `ViT-B-32/laion400m_e32`
- `RN50/openai`

### Specialized:
- `RN50x4/openai` (High resolution)
- `RN50x16/openai` (Very high resolution)
- `RN50x64/openai` (Ultra high resolution)

To see all models:
```bash
curl -u :jbone3311 https://briefly-charleston-verified-individuals.trycloudflare.com/interrogator/models | python -m json.tool
```

---

## 🎯 Analysis Modes

Your API supports these analysis modes:

| Mode | Speed | Quality | Best For |
|------|-------|---------|----------|
| **best** | ⚡ Slow | ⭐⭐⭐ Excellent | Production, final prompts |
| **fast** | ⚡⚡⚡ Fast | ⭐⭐ Good | Quick previews, testing |
| **classic** | ⚡⚡ Medium | ⭐⭐ Good | Traditional CLIP analysis |
| **negative** | ⚡⚡ Medium | ⭐⭐⭐ Excellent | Stable Diffusion negative prompts |
| **caption** | ⚡⚡⚡ Fast | ⭐⭐ Good | Simple image descriptions |

### Example Configurations:

**Fast Preview:**
```bash
CLIP_MODES=fast
```

**Production Quality:**
```bash
CLIP_MODES=best,negative
```

**Complete Analysis:**
```bash
CLIP_MODES=best,fast,classic,negative,caption
```

---

## 🐛 Troubleshooting

### Problem: "Authentication failed"

**Solutions:**
1. Check password in `.env`:
   ```bash
   grep CLIP_API_PASSWORD .env
   ```

2. Test password manually:
   ```bash
   python scripts/test_clip_api_auth.py https://briefly-charleston-verified-individuals.trycloudflare.com jbone3311
   ```

3. Verify API is accessible:
   ```bash
   curl https://briefly-charleston-verified-individuals.trycloudflare.com/
   ```

---

### Problem: "Cannot connect to CLIP API"

**Solutions:**
1. Check if tunnel is running
2. Verify URL is correct (no trailing slash)
3. Test with browser:
   ```
   https://briefly-charleston-verified-individuals.trycloudflare.com
   ```

---

### Problem: "Session expired"

**Solution:** The analyzer handles this automatically! It will:
- Detect expired session
- Re-authenticate
- Retry the request

No action needed on your part.

---

### Problem: "Model not found"

**Solutions:**
1. List available models:
   ```bash
   python scripts/test_clip_api_auth.py
   ```

2. Use a valid model name:
   ```bash
   # Good
   CLIP_MODEL_NAME=ViT-L-14/openai
   
   # Bad  
   CLIP_MODEL_NAME=ViT-L-14  # Missing /openai
   ```

---

## 🔒 Security Notes

### Best Practices:

1. **Never commit `.env` file:**
   ```bash
   # Already in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables:**
   ```bash
   # Good - read from environment
   password = os.getenv("CLIP_API_PASSWORD")
   
   # Bad - hardcoded
   password = "jbone3311"
   ```

3. **Keep Cloudflare URL private:**
   - Your tunnel URL gives access to your API
   - Don't share publicly
   - Consider local access instead

---

## 🚀 Next Steps

### 1. Batch Processing

Process multiple images:

```python
from src.processors import DirectoryProcessor
from src.database.db_manager import DatabaseManager
from src.analyzers.llm_manager import LLMManager

# Initialize
db_manager = DatabaseManager()
llm_manager = LLMManager()

# Configure
config = {
    'ENABLE_CLIP_ANALYSIS': True,
    'CLIP_API_URL': 'https://briefly-charleston-verified-individuals.trycloudflare.com',
    'CLIP_API_PASSWORD': 'jbone3311',
    'IMAGE_DIRECTORY': 'Images',
    'OUTPUT_DIRECTORY': 'Output'
}

# Process directory
processor = DirectoryProcessor(config, db_manager, llm_manager)
processor.process_directory()
```

### 2. Web Interface

Use the web interface with authentication:

```bash
# Make sure .env is configured
python run_web.py
```

Then open `http://localhost:5050` in your browser.

### 3. Integration

Integrate with your existing code - authentication is transparent!

---

## 📚 Additional Resources

- **API Documentation:** `CLIP_API_GUIDE.md`
- **Pinokio Setup:** `PINOKIO_API_SETUP.md`
- **Test Script:** `scripts/test_clip_api_auth.py`
- **Main README:** `README.md`

---

## ✅ Summary

Your CLIP analyzer now:
- ✅ Supports authenticated APIs (Forge/Pinokio)
- ✅ Manages sessions automatically
- ✅ Caches authentication for efficiency
- ✅ Works with 87 CLIP models
- ✅ 100% backward compatible
- ✅ Ready for production use!

**Just set your `.env` and you're good to go!** 🎉
