import os
import base64
import json
import logging
import requests

# Set up logging for the test
logging.basicConfig(level=logging.DEBUG)

# Test configuration
TEST_OPENAI_API_KEY = os.getenv('TEST_OPENAI_API_KEY', 'sk-proj-CSugxHuYq4dgiIEJjQo3T3BlbkFJimzWdOKu0UR9ZbHYvT2W')  # Replace with your actual OpenAI API key
TEST_IMAGE_PATH = r"C:\Users\jiml\Dropbox\#AIArt\SourceCode\CODE_CLIP_Analysis\Images\1\RANDOS (30).png"
TEST_PROMPT_TEXT = "What's in this image?"
TEST_MODEL = "gpt-4o"
TEST_TEMPERATURE = 0.7
TEST_MAX_TOKENS = 300

def encode_image(image_path):
    """Encode an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_llm_analysis():
    # Set the OpenAI API key in environment variable
    os.environ['OPENAI_API_KEY'] = TEST_OPENAI_API_KEY

    # Encode the image to base64
    base64_image = encode_image(TEST_IMAGE_PATH)

    # Create the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    # Create the data payload
    payload = {
        "model": TEST_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": TEST_PROMPT_TEXT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": TEST_TEMPERATURE,
        "max_tokens": TEST_MAX_TOKENS,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

    # Log the data payload excluding the 'messages' content
    logging.debug(f"Created data payload for LLM request: {json.dumps({k: v for k, v in payload.items() if k != 'messages'}, indent=2)}")

    # Send the request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Print the response
    if response.status_code == 200:
        print("Response received:")
        print(response.json())
    else:
        logging.error(f"Request failed: {response.json()}")
        print("No response received.")

if __name__ == "__main__":
    test_llm_analysis()
