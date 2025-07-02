import pytest
import os
import tempfile
import shutil
import json
import base64
from PIL import Image
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator
import sqlite3

@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_image_path(temp_dir: str) -> str:
    """Create a sample test image."""
    image_path = os.path.join(temp_dir, "test_image.jpg")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_path, "JPEG")
    
    return image_path

@pytest.fixture
def sample_png_image_path(temp_dir: str) -> str:
    """Create a sample PNG test image."""
    image_path = os.path.join(temp_dir, "test_image.png")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(image_path, "PNG")
    
    return image_path

@pytest.fixture
def multiple_test_images(temp_dir: str) -> list:
    """Create multiple test images for batch processing tests."""
    images = []
    colors = ['red', 'green', 'blue', 'yellow']
    
    for i, color in enumerate(colors):
        image_path = os.path.join(temp_dir, f"test_image_{i}.jpg")
        img = Image.new('RGB', (50, 50), color=color)
        img.save(image_path, "JPEG")
        images.append(image_path)
    
    return images

@pytest.fixture
def sample_env_file(temp_dir: str) -> str:
    """Create a sample .env file for testing."""
    env_path = os.path.join(temp_dir, ".env")
    env_content = """
# API Configuration
API_BASE_URL=http://localhost:7860
TIMEOUT=30

# CLIP Settings
CLIP_MODEL_NAME=ViT-L-14/openai
ENABLE_CLIP_ANALYSIS=true
ENABLE_CAPTION=true
ENABLE_BEST=true
ENABLE_FAST=true
ENABLE_CLASSIC=false
ENABLE_NEGATIVE=false

# LLM Settings
ENABLE_LLM_ANALYSIS=true
LLM_1_TITLE=Test GPT
LLM_1_API_URL=https://api.openai.com/v1/chat/completions
LLM_1_API_KEY=test_key_123
LLM_1_MODEL=gpt-4-vision-preview

# Processing Settings
IMAGE_DIRECTORY=test_images
OUTPUT_DIRECTORY=test_output
USE_JSON=true
USE_DATABASE=false
RETRY_LIMIT=3

# Emojis
EMOJI_SUCCESS=✅
EMOJI_WARNING=⚠️
EMOJI_ERROR=❌
EMOJI_INFO=ℹ️
EMOJI_PROCESSING=🔄
EMOJI_START=🚀
EMOJI_COMPLETE=🎉
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    return env_path

@pytest.fixture
def sample_llm_prompts(temp_dir: str) -> str:
    """Create a sample LLM_Prompts.json file for testing."""
    prompts_path = os.path.join(temp_dir, "LLM_Prompts.json")
    prompts_data = {
        "TEST_PROMPT1": {
            "TITLE": "Test Description",
            "PROMPT_TEXT": "Describe this test image in detail.",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 500
        },
        "TEST_PROMPT2": {
            "TITLE": "Test Analysis",
            "PROMPT_TEXT": "Analyze this test image from an artistic perspective.",
            "TEMPERATURE": 0.8,
            "MAX_TOKENS": 750
        }
    }
    
    with open(prompts_path, 'w') as f:
        json.dump(prompts_data, f, indent=4)
    
    return prompts_path

@pytest.fixture
def mock_clip_response() -> Dict[str, Any]:
    """Mock response from CLIP API."""
    return {
        "model": "ViT-L-14",
        "caption": "A test image with red background",
        "prompt": "red background, simple, test image",
        "score": 0.85
    }

@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """Mock response from LLM API."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1699999999,
        "model": "gpt-4-vision-preview",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test image with a red background. It appears to be a simple solid color image created for testing purposes."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def sample_json_output(temp_dir: str, sample_image_path: str) -> str:
    """Create a sample JSON output file for testing."""
    json_path = os.path.join(temp_dir, "test_output.json")
    json_data = {
        "image": sample_image_path,
        "model": "test-model",
        "prompts": {
            "results": [
                {
                    "prompt": "TEST_PROMPT1",
                    "result": {
                        "choices": [{"message": {"content": "Test description"}}]
                    }
                }
            ]
        },
        "analysis": {
            "best": "test prompt",
            "fast": "quick test",
            "caption": "test image"
        }
    }
    
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=4)
    
    return json_path

@pytest.fixture
def mock_database(temp_dir: str) -> str:
    """Create a mock SQLite database for testing."""
    db_path = os.path.join(temp_dir, "test_database.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables (based on db_utils.py structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            date_created REAL NOT NULL,
            file_size INTEGER NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            prompt TEXT,
            result TEXT NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images (id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path

@pytest.fixture
def image_base64() -> str:
    """Generate a base64 encoded test image."""
    # Create a simple image in memory
    img = Image.new('RGB', (10, 10), color='green')
    import io
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    return base64.b64encode(img_buffer.read()).decode('utf-8')

@pytest.fixture
def mock_requests_session():
    """Mock requests session for API testing."""
    with patch('requests.Session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing directory processor."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = '{"test": "output"}'
        mock_run.return_value.stderr = ''
        mock_run.return_value.returncode = 0
        yield mock_run