import requests  # Import the requests library to make HTTP requests
import base64  # Import base64 for encoding images
import os  # Import os for file path operations
import json  # Import json for handling JSON data

def encode_image_to_base64(image_path: str) -> str:
    """
    Encodes an image file to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:  # Open the image file in binary read mode
        return base64.b64encode(image_file.read()).decode('utf-8')  # Encode the image and decode to UTF-8 string

def save_json(data, filename: str):
    """
    Saves data to a JSON file.

    Args:
        data: The data to save (usually a dictionary).
        filename (str): The name of the file to save the data to.
    """
    with open(filename, 'w') as f:  # Open the file in write mode
        json.dump(data, f, indent=4)  # Write the data to the file in JSON format with indentation
    print(f"Saved output to {filename}")  # Print confirmation of save

def analyze_image(image_path: str, api_base_url: str, model: str, timeout: int = 60):
    """
    Sends an image to the CLIP API for analysis.

    Args:
        image_path (str): The path to the image file.
        api_base_url (str): The base URL of the API.
        model (str): The model name to use for analysis.
        timeout (int): The timeout for the API request (default is 60 seconds).

    Returns:
        dict: The JSON response from the API containing analysis results.
    """
    image_base64 = encode_image_to_base64(image_path)  # Encode the image to base64
    
    # Prepare the payload for the API request
    payload = {
        "image": image_base64,  # The base64 encoded image
        "model": model  # The model to use for analysis
    }
    
    headers = {"Content-Type": "application/json"}  # Set the content type to JSON
    
    # Make a POST request to the API for analysis
    response = requests.post(
        f"{api_base_url}/interrogator/analyze",  # API endpoint for analysis
        json=payload,  # The payload containing the image and model
        headers=headers,  # The headers for the request
        timeout=timeout  # Timeout for the request
    )
    response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
    return response.json()  # Return the JSON response from the API

def prompt_image(image_path: str, api_base_url: str, model: str, mode: str, timeout: int = 60):
    """
    Sends an image to the CLIP API to generate a prompt.

    Args:
        image_path (str): The path to the image file.
        api_base_url (str): The base URL of the API.
        model (str): The model name to use for generating prompts.
        mode (str): The mode for prompt generation (e.g., 'fast', 'best').
        timeout (int): The timeout for the API request (default is 60 seconds).

    Returns:
        dict: The JSON response from the API containing prompt results.
    """
    image_base64 = encode_image_to_base64(image_path)  # Encode the image to base64
    
    # Prepare the payload for the API request
    payload = {
        "image": image_base64,  # The base64 encoded image
        "model": model,  # The model to use for generating prompts
        "mode": mode  # The mode for prompt generation
    }
    
    headers = {"Content-Type": "application/json"}  # Set the content type to JSON
    
    # Make a POST request to the API for prompt generation
    response = requests.post(
        f"{api_base_url}/interrogator/prompt",  # API endpoint for prompt generation
        json=payload,  # The payload containing the image, model, and mode
        headers=headers,  # The headers for the request
        timeout=timeout  # Timeout for the request
    )
    response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
    return response.json()  # Return the JSON response from the API

def main():
    # Configuration
    api_base_url = "http://localhost:7860"  # Change if your API runs on a different URL
    model = "ViT-L-14"  # Change to the model you are using
    mode = "fast"  # Mode for prompt; can be 'fast', 'best', 'classic', 'negative', 'caption'
    image_filename = "test.png"  # Replace with your image filename
    
    # Check if image exists
    if not os.path.isfile(image_filename):  # Verify that the image file exists
        print(f"Image file {image_filename} not found in the current directory.")
        return
    
    # Analyze the image
    try:
        analysis_result = analyze_image(image_filename, api_base_url, model)
        save_json(analysis_result, "analyze_output.json")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
    
    # Generate prompt from the image
    try:
        prompt_result = prompt_image(image_filename, api_base_url, model, mode)
        save_json(prompt_result, "prompt_output.json")
    except Exception as e:
        print(f"An error occurred during prompt generation: {e}")

if __name__ == "__main__":
    main()