# Pinokio CLIP API Setup Guide

## 🔍 Current Status

Your Pinokio service at `https://briefly-charleston-verified-individuals.trycloudflare.com` is running but requires authentication.

**What we found:**
- ✅ Service is running via Cloudflare tunnel
- ⚠️ Requires login at `/pinokio/login`
- ⚠️ API endpoints may be under `/pinokio/` path
- ⚠️ Authentication needed before API access

---

## 🔐 Authentication Required

The service is redirecting to a login page, which means you need to:

1. **Set up authentication** in Pinokio
2. **Get an API token** or session cookie
3. **Configure authentication** in your project

---

## 🎯 Next Steps

### Option 1: Find the Correct API Path

Pinokio services often expose APIs under specific paths. Try these common patterns:

```bash
# Check if API is under /api/
curl https://briefly-charleston-verified-individuals.trycloudflare.com/api/health

# Check if API is under /pinokio/api/
curl https://briefly-charleston-verified-individuals.trycloudflare.com/pinokio/api/health

# Check if CLIP is under /clip/
curl https://briefly-charleston-verified-individuals.trycloudflare.com/clip/health

# Check the root documentation
curl https://briefly-charleston-verified-individuals.trycloudflare.com/
```

### Option 2: Check Pinokio Configuration

1. **Open Pinokio Interface:**
   - Navigate to `https://briefly-charleston-verified-individuals.trycloudflare.com`
   - Log in to the Pinokio dashboard
   - Look for the CLIP service configuration

2. **Find API Endpoints:**
   - Check the service settings
   - Look for "API" or "Endpoints" section
   - Note the base path for CLIP interrogator

3. **Get Authentication Token:**
   - Check if there's an API token setting
   - Look for authentication credentials
   - May need to generate an API key

### Option 3: Disable Authentication (Local Only)

If this is running locally through Pinokio:

1. Open Pinokio settings
2. Find the CLIP service
3. Look for authentication settings
4. Disable authentication or allow local access

---

## 📊 Common Pinokio API Patterns

### Pattern 1: Direct API Access
```
https://your-domain.trycloudflare.com/api/endpoint
```

### Pattern 2: Service-Based Path
```
https://your-domain.trycloudflare.com/services/clip/endpoint
```

### Pattern 3: Application Path
```
https://your-domain.trycloudflare.com/pinokio/services/clip/endpoint
```

### Pattern 4: Port-Based Access
```
https://your-domain.trycloudflare.com:7860/endpoint
```

---

## 🔧 Configuration Options

### For Authenticated API

Once you find the correct path and get authentication:

**.env configuration:**
```bash
# CLIP API with authentication
CLIP_API_URL=https://briefly-charleston-verified-individuals.trycloudflare.com/api
CLIP_API_TOKEN=your_api_token_here
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,negative
CLIP_API_TIMEOUT=300
```

### For Direct CLIP Service

If CLIP is accessible without Pinokio wrapper:

**.env configuration:**
```bash
# Direct CLIP service
CLIP_API_URL=http://localhost:7860
CLIP_MODEL_NAME=ViT-L-14/openai
CLIP_MODES=best,fast,negative
CLIP_API_TIMEOUT=300
```

---

## 🐛 Troubleshooting

### Issue: Redirecting to Login

**Current Error:**
```
Found. Redirecting to /pinokio/login
```

**Solutions:**

1. **Login to Pinokio first:**
   - Open browser: `https://briefly-charleston-verified-individuals.trycloudflare.com`
   - Log in to the dashboard
   - Check service status

2. **Get API documentation:**
   - Look in Pinokio interface for API docs
   - Check CLIP service settings
   - Find the correct endpoint paths

3. **Check local access:**
   - If Pinokio is running locally, try: `http://localhost:7860`
   - May not need authentication for local access

4. **Use API token:**
   - Generate token in Pinokio settings
   - Add to requests: `Authorization: Bearer YOUR_TOKEN`

---

## 🔍 Investigation Commands

Run these to discover the correct configuration:

```bash
# 1. Check what's at the root
curl -L https://briefly-charleston-verified-individuals.trycloudflare.com/

# 2. Try common API paths
curl https://briefly-charleston-verified-individuals.trycloudflare.com/api/
curl https://briefly-charleston-verified-individuals.trycloudflare.com/clip/
curl https://briefly-charleston-verified-individuals.trycloudflare.com/interrogator/

# 3. Check if local access works
curl http://localhost:7860/health
curl http://127.0.0.1:7860/health

# 4. Try with session cookie (after manual login)
# Get cookie from browser after logging in
curl -H "Cookie: connect.sid=YOUR_SESSION_ID" \
  https://briefly-charleston-verified-individuals.trycloudflare.com/health
```

---

## 📝 What to Look For

When you log into the Pinokio interface, check for:

1. **Service Status:**
   - Is CLIP service running?
   - What port is it on?
   - Any error messages?

2. **API Information:**
   - API endpoint URLs
   - Authentication requirements
   - Available operations

3. **Configuration:**
   - Base URL for API calls
   - Required headers
   - Authentication tokens

4. **Documentation:**
   - Links to API docs
   - Example requests
   - Supported models/modes

---

## ✅ Once You Have the Details

After finding the correct configuration:

1. **Update `.env` file:**
   ```bash
   CLIP_API_URL=<correct_url_here>
   CLIP_API_TOKEN=<token_if_needed>
   CLIP_MODEL_NAME=ViT-L-14/openai
   CLIP_MODES=best,fast,negative
   ```

2. **Test with our script:**
   ```bash
   python scripts/test_clip_api.py YOUR_CORRECT_URL
   ```

3. **Start processing images:**
   ```bash
   python main.py
   ```

---

## 🆘 Need Help?

**What to provide:**

1. Screenshot of Pinokio dashboard
2. CLIP service settings from Pinokio
3. Any API documentation links
4. Output of: `curl -L https://briefly-charleston-verified-individuals.trycloudflare.com/`

**Where to look in Pinokio:**

- Settings → Services → CLIP
- API → Endpoints
- Authentication → Tokens
- Documentation → API Reference

---

## 🔄 Alternative: Local API Access

If the Cloudflare tunnel is just for remote access, you might have local access without authentication:

```bash
# Try local access (if Pinokio is running locally)
python scripts/test_clip_api.py http://localhost:7860
```

If this works, you can use:
```bash
CLIP_API_URL=http://localhost:7860
```

This avoids the authentication requirement of the Cloudflare tunnel.

---

**Next Action:** Log into your Pinokio dashboard to find the correct API configuration! 🔍
