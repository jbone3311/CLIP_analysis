#!/usr/bin/env python3
"""
CLIP API Service for Image Analysis
Provides REST API endpoints for CLIP interrogator functionality
"""

import os
import base64
import json
import logging
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from PIL import Image
import io
import torch
from clip_interrogator import Config, Interrogator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global interrogator instance
interrogator = None

def initialize_interrogator():
    """Initialize the CLIP interrogator"""
    global interrogator
    try:
        config = Config()
        config.clip_model_name = "ViT-L-14/openai"
        config.clip_pretrained_model_name = None
        config.projection_path = None
        config.interrogator_model_name = "ViT-L-14/openai"
        config.interrogator_pretrained_model_name = None
        config.projection_path = None
        config.device = "cuda" if torch.cuda.is_available() else "cpu"
        config.cache_path = None
        config.download_cache = True
        config.chunk_size = 2048
        config.flavor_intermediate_count = 2048
        config.truncate = True
        
        interrogator = Interrogator(config)
        logger.info(f"CLIP Interrogator initialized on device: {config.device}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize CLIP Interrogator: {e}")
        return False

def decode_base64_image(image_base64: str) -> Image.Image:
    """Decode base64 image string to PIL Image"""
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "CLIP Interrogator API",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "interrogator_ready": interrogator is not None
    })

@app.route('/interrogator/analyze', methods=['POST'])
def analyze_image():
    """Analyze image endpoint"""
    try:
        if interrogator is None:
            return jsonify({"error": "CLIP Interrogator not initialized"}), 500
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400
        
        # Decode base64 image
        image = decode_base64_image(data['image'])
        
        # Get model (optional, defaults to interrogator's model)
        model = data.get('model', None)
        
        # Analyze image
        logger.info("Starting image analysis...")
        result = interrogator.interrogate(image)
        
        return jsonify({
            "status": "success",
            "result": result,
            "model": model or "ViT-L-14/openai"
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/interrogator/prompt', methods=['POST'])
def generate_prompt():
    """Generate prompt endpoint"""
    try:
        if interrogator is None:
            return jsonify({"error": "CLIP Interrogator not initialized"}), 500
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400
        
        # Decode base64 image
        image = decode_base64_image(data['image'])
        
        # Get parameters
        mode = data.get('mode', 'fast')
        model = data.get('model', None)
        
        # Generate prompt based on mode
        if mode == 'fast':
            result = interrogator.interrogate_fast(image)
        elif mode == 'best':
            result = interrogator.interrogate(image)
        elif mode == 'classic':
            result = interrogator.interrogate_classic(image)
        elif mode == 'negative':
            result = interrogator.interrogate_negative(image)
        elif mode == 'caption':
            result = interrogator.interrogate_caption(image)
        else:
            return jsonify({"error": f"Invalid mode: {mode}"}), 400
        
        return jsonify({
            "status": "success",
            "result": result,
            "mode": mode,
            "model": model or "ViT-L-14/openai"
        })
        
    except Exception as e:
        logger.error(f"Prompt generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    models = [
        "ViT-L-14/openai",
        "ViT-B-32/openai", 
        "ViT-B-16/openai",
        "ViT-L-14/laion2b_s32b_b82k",
        "ViT-B-32/laion2b_s34b_b79k"
    ]
    return jsonify({
        "models": models,
        "current_model": "ViT-L-14/openai"
    })

@app.route('/modes', methods=['GET'])
def list_modes():
    """List available modes"""
    modes = [
        "fast",
        "best", 
        "classic",
        "negative",
        "caption"
    ]
    return jsonify({"modes": modes})

if __name__ == '__main__':
    print("🚀 Starting CLIP API Service...")
    print("=" * 50)
    
    # Initialize interrogator
    if initialize_interrogator():
        print("✅ CLIP Interrogator initialized successfully")
        print(f"🔧 Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        print(f"🌐 API will be available at: http://localhost:7860")
        print("=" * 50)
        
        # Start Flask app
        app.run(host='0.0.0.0', port=7860, debug=False)
    else:
        print("❌ Failed to initialize CLIP Interrogator")
        exit(1) 