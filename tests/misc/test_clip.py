#!/usr/bin/env python3
"""
Test CLIP Analysis
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.analyzers.clip_analyzer import process_image_with_clip

def test_clip_analysis():
    """Test CLIP analysis on a sample image"""
    print("Testing CLIP Analysis...")
    
    # Test image path
    test_image = "Images/Group/Photo (1).png"
    
    if not os.path.exists(test_image):
        print(f"Test image not found: {test_image}")
        return False
    
    print(f"Using test image: {test_image}")
    
    # CLIP configuration
    api_base_url = "http://localhost:7860"
    model = "ViT-L-14/openai"
    modes = ["best", "fast"]
    
    try:
        # Test CLIP service health first
        print("Checking CLIP service health...")
        health_response = requests.get(f"{api_base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ CLIP service is healthy")
        else:
            print(f"❌ CLIP service health check failed: {health_response.status_code}")
            return False
        
        # Test CLIP analysis
        print("Running CLIP analysis...")
        result = process_image_with_clip(
            image_path=test_image,
            api_base_url=api_base_url,
            model=model,
            modes=modes,
            force_reprocess=True
        )
        
        if result.get("status") == "success":
            print("✅ CLIP analysis completed successfully!")
            
            # Print some results
            analysis_results = result.get("analysis_results", {})
            if analysis_results:
                print("\nCLIP Analysis Results:")
                for mode, mode_result in analysis_results.items():
                    if isinstance(mode_result, dict) and "prompt" in mode_result:
                        print(f"  {mode}: {mode_result['prompt']}")
            
            return True
        else:
            print(f"❌ CLIP analysis failed: {result.get('message', 'Unknown error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to CLIP service. Is it running on port 7860?")
        return False
    except Exception as e:
        print(f"❌ Error during CLIP analysis: {e}")
        return False

if __name__ == "__main__":
    success = test_clip_analysis()
    if success:
        print("\n🎉 CLIP analysis is working correctly!")
    else:
        print("\n💥 CLIP analysis test failed!")
        sys.exit(1) 