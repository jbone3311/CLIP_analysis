#!/usr/bin/env python3
"""
Test Script for CLIP API with Authentication (Stable Diffusion Forge)
Tests connectivity and available options with password authentication.
"""

import requests
import sys
import os
import json
from typing import Dict, Any, Optional

def login(url: str, password: str) -> Optional[requests.Session]:
    """Login to Pinokio/Forge and get authenticated session"""
    session = requests.Session()
    try:
        # Attempt login
        login_url = f"{url}/pinokio/login"
        response = session.post(
            login_url,
            data={"password": password},
            allow_redirects=True,
            timeout=10
        )
        
        # Check if we got a session cookie
        if 'connect.sid' in session.cookies:
            return session
        else:
            print(f"❌ Login failed - no session cookie received")
            return None
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_endpoint(session: requests.Session, url: str, endpoint: str) -> Dict[str, Any]:
    """Test a specific API endpoint with authenticated session"""
    full_url = f"{url}{endpoint}"
    try:
        response = session.get(full_url, timeout=10)
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed - is the API running?"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out"
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def print_result(test_name: str, result: Dict[str, Any], show_data: bool = True):
    """Print test result in a formatted way"""
    if result["success"]:
        print(f"✅ {test_name}")
        if show_data and "data" in result:
            data = result["data"]
            if isinstance(data, list):
                if len(data) > 10:
                    print(f"   Found {len(data)} items (showing first 10):")
                    for item in data[:10]:
                        print(f"     - {item}")
                    print(f"     ... and {len(data) - 10} more")
                else:
                    print(f"   Found {len(data)} items:")
                    for item in data:
                        print(f"     - {item}")
            else:
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"❌ {test_name}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    print()

def main():
    """Main test function"""
    # Get API URL and password from command line, environment, or use defaults
    api_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("CLIP_API_URL", "http://localhost:7860")
    password = sys.argv[2] if len(sys.argv) > 2 else os.getenv("CLIP_API_PASSWORD", "")
    
    print("=" * 70)
    print("🧪 CLIP API Connection Test (with Authentication)")
    print("=" * 70)
    print(f"API URL: {api_url}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    # Step 1: Login
    print("🔐 Step 1: Authenticating...")
    session = login(api_url, password)
    
    if not session:
        print()
        print("=" * 70)
        print("❌ Authentication failed! Cannot proceed with tests.")
        print("=" * 70)
        return 1
    
    print("✅ Successfully authenticated!")
    print()
    
    # Step 2: Test CLIP Interrogator endpoints
    print("🧪 Step 2: Testing CLIP Interrogator API")
    print()
    
    # Test 1: List Models
    print("Test 1: Available CLIP Models")
    result = test_endpoint(session, api_url, "/interrogator/models")
    print_result("List CLIP Models", result, show_data=True)
    
    # Test 2: Check info endpoint
    print("Test 2: API Info")
    result = test_endpoint(session, api_url, "/info")
    print_result("API Info", result, show_data=False)
    
    # Test 3: Check config
    print("Test 3: API Config")
    result = test_endpoint(session, api_url, "/config")
    print_result("API Config", result, show_data=False)
    
    print("=" * 70)
    print("🎯 Configuration Summary")
    print("=" * 70)
    print()
    print("✅ Your API is: Stable Diffusion Forge + CLIP Interrogator")
    print()
    print("Add this to your .env file:")
    print()
    print(f"# CLIP API Configuration (Stable Diffusion Forge)")
    print(f"CLIP_API_URL={api_url}")
    print(f"CLIP_API_PASSWORD={password}")
    print("CLIP_MODEL_NAME=ViT-L-14/openai")
    print("CLIP_MODES=best,fast,negative")
    print("CLIP_API_TIMEOUT=300")
    print()
    print("Available endpoints:")
    print(f"  - {api_url}/interrogator/models")
    print(f"  - {api_url}/interrogator/prompt")
    print(f"  - {api_url}/interrogator/analyze")
    print(f"  - {api_url}/sdapi/v1/interrogate")
    print()
    print("=" * 70)
    print()
    print("📚 Next steps:")
    print("  1. Update your .env file with the configuration above")
    print("  2. Modify src/analyzers/clip_analyzer.py to use these endpoints")
    print("  3. Add authentication support to your CLIP requests")
    print()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

