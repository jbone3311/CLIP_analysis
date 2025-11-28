#!/usr/bin/env python3
"""
Quick Test Script for CLIP API Connection
Tests connectivity and available options at your CLIP API endpoint.
"""

import requests
import sys
import os
import json
from typing import Dict, Any

def test_endpoint(url: str, endpoint: str, method: str = 'GET') -> Dict[str, Any]:
    """Test a specific API endpoint"""
    full_url = f"{url}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(full_url, timeout=10)
        else:
            response = requests.post(full_url, timeout=10)
        
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

def print_result(test_name: str, result: Dict[str, Any]):
    """Print test result in a formatted way"""
    if result["success"]:
        print(f"✅ {test_name}")
        if "data" in result:
            print(f"   Response: {json.dumps(result['data'], indent=2)}")
    else:
        print(f"❌ {test_name}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    print()

def main():
    """Main test function"""
    # Default API URL (can be overridden via command line or environment)
    api_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("CLIP_API_URL", "http://localhost:7860")
    
    print("=" * 70)
    print("🧪 CLIP API Connection Test")
    print("=" * 70)
    print(f"Testing API at: {api_url}")
    print()
    
    # Test 1: Health Check
    print("Test 1: Health Check")
    result = test_endpoint(api_url, "/health")
    print_result("Health Check", result)
    
    # Test 2: List Models
    print("Test 2: Available Models")
    result = test_endpoint(api_url, "/models")
    print_result("List Models", result)
    
    # Test 3: List Modes
    print("Test 3: Available Modes")
    result = test_endpoint(api_url, "/modes")
    print_result("List Modes", result)
    
    print("=" * 70)
    print("🎯 Configuration Summary")
    print("=" * 70)
    print()
    print("Add this to your .env file:")
    print()
    print(f"CLIP_API_URL={api_url}")
    print("CLIP_MODEL_NAME=ViT-L-14/openai")
    print("CLIP_MODES=best,fast,negative")
    print("CLIP_API_TIMEOUT=300")
    print()
    print("=" * 70)
    print()
    print("📚 For detailed configuration options, see: CLIP_API.md")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

