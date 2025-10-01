# CLIP API Configuration Guide

## 🌐 Your CLIP API Endpoint

**URL:** `https://briefly-charleston-verified-individuals.trycloudflare.com`

This guide explains all available API options and how to configure your project to use them.

---

## 🔌 Available API Endpoints

### 1. Health Check
**Endpoint:** `GET /health`

Check if the CLIP service is running and ready.

**Response:**
```json
{
  "status": "healthy",
  "service": "CLIP Interrogator API",
  "device": "cuda",
  "interrogator_ready": true
}
```

**Test it:**
```bash
curl https://briefly-charleston-verified-individuals.trycloudflare.com/health
```

---

### 2. List Available Models
**Endpoint:** `GET /models`

Get all available CLIP models.

**Response:**
```json
{
  "models": [
    "ViT-L-14/openai",
    "ViT-B-32/openai",
    "ViT-B-16/openai",
    "ViT-L-14/laion2b_s32b_b82k",
    "ViT-B-32/laion2b_s34b_b79k"
  ],
  "current_model": "ViT-L-14/openai"
}
```

**Test it:**
```bash
curl https://briefly-charleston-verified-individuals.trycloudflare.com/models
```

---

### 3. List Available Modes
**Endpoint:** `GET /modes`

Get all available analysis modes.

**Response:**
```json
{
  "modes": [
    "fast",
    "best",
    "classic",
    "negative",
    "caption"
  ]
}
```

**Test it:**
```bash
curl https://briefly-charleston-verified-individuals.trycloudflare.com/modes
```

---

### 4. Image Analysis
**Endpoint:** `POST /interrogator/analyze`

Analyze an image and get a comprehensive description.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "model": "ViT-L-14/openai"  // Optional, defaults to ViT-L-14/openai
}
```

**Response:**
```json
{
  "status": "success",
  "result": "a detailed description of the image...",
  "model": "ViT-L-14/openai"
}
```

---

### 5. Prompt Generation
**Endpoint:** `POST /interrogator/prompt`

Generate prompts for an image in different modes.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "mode": "best",  // Options: fast, best, classic, negative, caption
  "model": "ViT-L-14/openai"  // Optional
}
```

**Response:**
```json
{
  "status": "success",
  "result": "generated prompt based on mode...",
  "mode": "best",
  "model": "ViT-L-14/openai"
}
```

---

## ⚙️ Configuration Options

### Environment Variables

Add these to your `.env` file:

```bash
# CLIP API Configuration
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,classic,negative,caption
CLIP_API_TIMEOUT=300
```

### Configuration Details

#### **CLIP_API_URL**
- **Purpose:** Base URL for your CLIP API service
- **Default:** `http://localhost:7860`
- **Your Value:** `https://briefly-charleston-verified-individuals.trycloudflare.com`
- **Notes:** Remove trailing slash

#### **CLIP_MODEL_NAME**
- **Purpose:** Which CLIP model to use for analysis
- **Options:**
  - `ViT-L-14/openai` - Best quality (recommended)
  - `ViT-B-32/openai` - Balanced
  - `ViT-B-16/openai` - Fast
  - `ViT-L-14/laion2b_s32b_b82k` - Alternative large model
  - `ViT-B-32/laion2b_s34b_b79k` - Alternative base model
- **Default:** `ViT-L-14/openai`

#### **CLIP_MODES**
- **Purpose:** Which analysis modes to run
- **Options:**
  - `best` - Highest quality analysis (slower)
  - `fast` - Quick analysis (faster)
  - `classic` - Traditional CLIP interrogation
  - `negative` - Generate negative prompts
  - `caption` - Image captioning
- **Format:** Comma-separated list
- **Example:** `best,fast,classic,negative,caption`
- **Recommended:** `best,fast,negative` (good balance)

#### **CLIP_API_TIMEOUT**
- **Purpose:** Maximum seconds to wait for API response
- **Default:** `300` (5 minutes)
- **Range:** 60-600 seconds
- **Notes:** Increase for slower connections or large images

---

## 🚀 Quick Setup

### Step 1: Update Your `.env` File

```bash
# Copy the example file if you haven't already
cp secure_env_example.txt .env

# Edit .env and update these values:
nano .env
```

Add/update these lines:
```bash
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,negative
CLIP_API_TIMEOUT=300
```

### Step 2: Test the Connection

```bash
# Test API health
curl https://briefly-charleston-verified-individuals.trycloudflare.com/health

# Check available models
curl https://briefly-charleston-verified-individuals.trycloudflare.com/models

# Check available modes
curl https://briefly-charleston-verified-individuals.trycloudflare.com/modes
```

### Step 3: Test with Your Project

```bash
# Run the web interface
python main.py

# Or use the CLI
python main.py process --input Images --output Output
```

---

## 🎯 Usage Examples

### Example 1: Quick Analysis (Fast Mode Only)

**.env configuration:**
```bash
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_MODEL_NAME=ViT-B-32/openai
CLIP_MODES=fast
CLIP_API_TIMEOUT=60
```

**Best for:** Quick preview, testing, large batches

---

### Example 2: High Quality Analysis (Best + Negative)

**.env configuration:**
```bash
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,negative
CLIP_API_TIMEOUT=300
```

**Best for:** Production quality, Stable Diffusion prompts, detailed analysis

---

### Example 3: Complete Analysis (All Modes)

**.env configuration:**
```bash
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,classic,negative,caption
CLIP_API_TIMEOUT=600
```

**Best for:** Comprehensive analysis, comparison of different modes

---

## 🔍 Mode Comparison

| Mode | Speed | Quality | Use Case |
|------|-------|---------|----------|
| **fast** | ⚡⚡⚡ Fast | ⭐⭐ Good | Quick previews, testing |
| **best** | ⚡ Slow | ⭐⭐⭐ Excellent | Production, final prompts |
| **classic** | ⚡⚡ Medium | ⭐⭐ Good | Traditional CLIP analysis |
| **negative** | ⚡⚡ Medium | ⭐⭐⭐ Excellent | Stable Diffusion negative prompts |
| **caption** | ⚡⚡⚡ Fast | ⭐⭐ Good | Simple descriptions |

---

## 🧪 Testing Your Configuration

### Python Script Test

```python
import requests
import base64

# Your API URL
api_url = "https://briefly-charleston-verified-individuals.trycloudflare.com"

# Test health
response = requests.get(f"{api_url}/health")
print(f"Health Check: {response.json()}")

# Test models
response = requests.get(f"{api_url}/models")
print(f"Available Models: {response.json()}")

# Test modes
response = requests.get(f"{api_url}/modes")
print(f"Available Modes: {response.json()}")
```

### CLI Test

```bash
# Test a single image
python -m src.analyzers.clip_analyzer \
  your_image.jpg \
  --api_base_url https://briefly-charleston-verified-individuals.trycloudflare.com \
  --model ViT-L-14/openai \
  --modes best fast \
  --output test_result.json
```

---

## ⚠️ Troubleshooting

### Connection Issues

**Problem:** Cannot connect to API
```bash
ConnectionError: Cannot connect to CLIP API
```

**Solutions:**
1. Check if the Cloudflare tunnel is running
2. Verify the URL is correct (no trailing slash)
3. Test with curl: `curl https://briefly-charleston-verified-individuals.trycloudflare.com/health`
4. Check your internet connection

---

### Timeout Issues

**Problem:** Request takes too long
```bash
Timeout: CLIP API request timed out
```

**Solutions:**
1. Increase `CLIP_API_TIMEOUT` in .env
2. Use faster modes: `fast`, `caption`
3. Reduce number of modes
4. Check API server performance

---

### Model Issues

**Problem:** Model not available
```bash
Error: Model not found
```

**Solutions:**
1. Check available models: `curl https://briefly-charleston-verified-individuals.trycloudflare.com/models`
2. Update `CLIP_MODEL_NAME` to a valid model
3. Use default: `ViT-L-14/openai`

---

## 📊 Performance Tips

### For Speed:
- Use `fast` or `caption` modes only
- Use smaller models: `ViT-B-32/openai`
- Process fewer images at once
- Reduce timeout for quick failures

### For Quality:
- Use `best` and `negative` modes
- Use larger models: `ViT-L-14/openai`
- Increase timeout: `600` seconds
- Enable parallel processing

### For Balance:
- Use `fast,best,negative` modes
- Use `ViT-L-14/openai` model
- Set timeout: `300` seconds
- Enable incremental processing

---

## 🔐 Security Notes

1. **HTTPS:** Your Cloudflare tunnel uses HTTPS ✅
2. **Credentials:** No API key needed for CLIP service
3. **Data:** Images sent as base64 in POST requests
4. **Privacy:** Keep your tunnel URL private if sensitive

---

## 📚 Additional Resources

- **Project README:** `README.md`
- **Environment Example:** `secure_env_example.txt`
- **CLIP Analyzer:** `src/analyzers/clip_analyzer.py`
- **CLIP Service:** `src/services/clip_service.py`

---

## ✅ Configuration Checklist

- [ ] Updated `.env` with your Cloudflare tunnel URL
- [ ] Set `CLIP_API_URL` to your endpoint
- [ ] Chose appropriate `CLIP_MODEL_NAME`
- [ ] Selected `CLIP_MODES` based on your needs
- [ ] Set `CLIP_API_TIMEOUT` appropriately
- [ ] Tested connection with `/health` endpoint
- [ ] Verified available models with `/models`
- [ ] Ran test analysis with sample image
- [ ] Confirmed results in Output directory

---

**Your CLIP API is ready to use!** 🎉

For questions or issues, check the troubleshooting section or create an issue on GitHub.
