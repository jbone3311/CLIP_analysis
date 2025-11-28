# CLIP API Guide

This guide explains how to configure and use the CLIP API for image analysis. The system supports both authenticated and unauthenticated CLIP APIs.

## Quick Setup

1. **Configure your `.env` file:**
   ```bash
   CLIP_API_URL=http://localhost:7860
   CLIP_API_PASSWORD=                    # Only if your API requires authentication
   CLIP_MODEL_NAME=ViT-L-14/openai
   CLIP_MODES=best,fast,negative
   CLIP_API_TIMEOUT=300
   ```

2. **Test the connection:**
   ```bash
   python scripts/test_clip_api_auth.py
   ```

3. **Start analyzing images:**
   ```bash
   python -m src.analyzers.clip_analyzer Images/test.jpg
   ```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# CLIP API Configuration
CLIP_API_URL=http://localhost:7860              # Base URL for CLIP API
CLIP_API_PASSWORD=                              # Password for authenticated APIs (optional)
CLIP_MODEL_NAME=ViT-L-14/openai                # CLIP model to use
CLIP_MODES=best,fast,classic,negative,caption   # Analysis modes (comma-separated)
CLIP_API_TIMEOUT=300                            # Request timeout in seconds
```

### Configuration Details

#### CLIP_API_URL
- **Purpose:** Base URL for your CLIP API service
- **Default:** `http://localhost:7860`
- **Notes:** Remove trailing slash, use HTTPS for remote services

#### CLIP_API_PASSWORD
- **Purpose:** Password for authenticated APIs (Forge/Pinokio)
- **Required:** Only if your API requires authentication
- **Notes:** Leave empty if your API doesn't require authentication

#### CLIP_MODEL_NAME
- **Purpose:** Which CLIP model to use for analysis
- **Options:**
  - `ViT-L-14/openai` - Best quality (recommended)
  - `ViT-B-32/openai` - Balanced
  - `ViT-B-16/openai` - Fast
  - `ViT-L-14/laion2b_s32b_b82k` - Alternative large model
  - `ViT-B-32/laion2b_s34b_b79k` - Alternative base model
- **Default:** `ViT-L-14/openai`

#### CLIP_MODES
- **Purpose:** Which analysis modes to run
- **Options:**
  - `best` - Highest quality analysis (slower)
  - `fast` - Quick analysis (faster)
  - `classic` - Traditional CLIP interrogation
  - `negative` - Generate negative prompts
  - `caption` - Image captioning
- **Format:** Comma-separated list
- **Recommended:** `best,fast,negative` (good balance)

#### CLIP_API_TIMEOUT
- **Purpose:** Maximum seconds to wait for API response
- **Default:** `300` (5 minutes)
- **Range:** 60-600 seconds
- **Notes:** Increase for slower connections or large images

## Authentication

### Supported Authentication Methods

The system supports password-based authentication for APIs like Stable Diffusion Forge and Pinokio.

### How Authentication Works

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

### Setting Up Authentication

1. **Add password to `.env`:**
   ```bash
   CLIP_API_PASSWORD=your_password_here
   ```

2. **The system handles authentication automatically:**
   - No code changes needed
   - Session management is transparent
   - Works with all analysis modes

## API Endpoints

### Health Check
**Endpoint:** `GET /health`

Check if the CLIP service is running and ready.

**Test:**
```bash
curl http://localhost:7860/health
```

### List Available Models
**Endpoint:** `GET /models`

Get all available CLIP models.

**Test:**
```bash
curl http://localhost:7860/models
```

### List Available Modes
**Endpoint:** `GET /modes`

Get all available analysis modes.

**Test:**
```bash
curl http://localhost:7860/modes
```

### Image Analysis
**Endpoint:** `POST /interrogator/analyze`

Analyze an image and get a comprehensive description.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "model": "ViT-L-14/openai"
}
```

### Prompt Generation
**Endpoint:** `POST /interrogator/prompt`

Generate prompts for an image in different modes.

**Request Body:**
```json
{
  "image": "base64_encoded_image_string",
  "mode": "best",
  "model": "ViT-L-14/openai"
}
```

## Analysis Modes

| Mode | Speed | Quality | Use Case |
|------|-------|---------|----------|
| **fast** | ⚡⚡⚡ Fast | ⭐⭐ Good | Quick previews, testing |
| **best** | ⚡ Slow | ⭐⭐⭐ Excellent | Production, final prompts |
| **classic** | ⚡⚡ Medium | ⭐⭐ Good | Traditional CLIP analysis |
| **negative** | ⚡⚡ Medium | ⭐⭐⭐ Excellent | Stable Diffusion negative prompts |
| **caption** | ⚡⚡⚡ Fast | ⭐⭐ Good | Simple descriptions |

### Example Configurations

**Quick Preview:**
```bash
CLIP_MODES=fast
CLIP_MODEL_NAME=ViT-B-32/openai
CLIP_API_TIMEOUT=60
```

**Production Quality:**
```bash
CLIP_MODES=best,negative
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_API_TIMEOUT=300
```

**Complete Analysis:**
```bash
CLIP_MODES=best,fast,classic,negative,caption
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_API_TIMEOUT=600
```

## Usage Examples

### Command Line

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

### Programmatic Usage

```python
from src.analyzers.clip_analyzer import process_image_with_clip
import os

# Configuration from environment
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
    password=password  # Authentication happens automatically
)

if result["status"] == "success":
    print(f"✅ Analysis complete!")
    print(f"Prompts: {result['prompt']}")
else:
    print(f"❌ Error: {result['message']}")
```

## Performance Tips

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

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to API

**Solutions:**
1. Check if the API service is running
2. Verify the URL is correct (no trailing slash)
3. Test with curl: `curl http://localhost:7860/health`
4. Check your internet connection
5. For remote services, verify the tunnel/URL is accessible

### Authentication Issues

**Problem:** "Authentication failed"

**Solutions:**
1. Check password in `.env`:
   ```bash
   grep CLIP_API_PASSWORD .env
   ```

2. Test authentication:
   ```bash
   python scripts/test_clip_api_auth.py
   ```

3. Verify API is accessible:
   - Check if service requires authentication
   - Verify password is correct
   - Check API documentation for auth requirements

### Timeout Issues

**Problem:** Request takes too long

**Solutions:**
1. Increase `CLIP_API_TIMEOUT` in `.env`
2. Use faster modes: `fast`, `caption`
3. Reduce number of modes
4. Check API server performance

### Model Issues

**Problem:** Model not available

**Solutions:**
1. Check available models:
   ```bash
   curl http://localhost:7860/models
   ```

2. Update `CLIP_MODEL_NAME` to a valid model
3. Use default: `ViT-L-14/openai`

### Session Expired

**Problem:** "Session expired"

**Solution:** The analyzer handles this automatically! It will:
- Detect expired session
- Re-authenticate
- Retry the request

No action needed on your part.

## Security Notes

1. **Never commit `.env` file:**
   - Already in `.gitignore`
   - Contains sensitive passwords and keys

2. **Use environment variables:**
   - Never hardcode passwords in code
   - Always read from environment

3. **Keep URLs private:**
   - Tunnel URLs give access to your API
   - Don't share publicly
   - Consider local access when possible

4. **HTTPS for remote services:**
   - Use HTTPS for remote API access
   - Verify SSL certificates

## Testing

### Quick Test

```bash
# Test authentication and API access
python scripts/test_clip_api_auth.py
```

### Test with Real Image

```bash
# Analyze the test image
python -m src.analyzers.clip_analyzer Images/test.jpg
```

### Python Script Test

```python
import requests

# Your API URL from environment
api_url = os.getenv("CLIP_API_URL", "http://localhost:7860")

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

## Related Files

- `CONFIG.md` - General configuration guide
- `secure_env_example.txt` - Template for `.env` file
- `src/analyzers/clip_analyzer.py` - CLIP analyzer implementation
- `src/services/clip_service.py` - CLIP service wrapper
- `scripts/test_clip_api_auth.py` - Authentication test script

## Additional Resources

- **Project README:** `README.md`
- **Configuration Guide:** `CONFIG.md`
- **Development:** `DEVELOPMENT_NOTES.md`

---

**Your CLIP API is ready to use!** 🎉

For questions or issues, check the troubleshooting section or review the documentation.

